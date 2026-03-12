"""Agent router — routes candidate queries through a ReAct tool-use loop.

Each agent is a persona with access to specific data tables. Instead of
picking from rigid skill functions, the agent iteratively calls generic data
tools (query_table, read_document, describe_tables) until it has enough
context to answer the question, then formulates a response with an appropriate
display format.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from agent_tools.tools import (
    TOOL_DEFINITIONS,
    describe_tables,
    query_table,
    read_document,
)
from llm_interface.llm_client import LLMClient
from telemetry_layer.telemetry import VALID_AGENTS

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────
# Agent Personas
# ────────────────────────────────────────────────────

AGENT_PROMPTS: dict[str, str] = {
    "analyst": (
        "You are Priya, Senior Data Analyst at FoodDash (2 years on the team). "
        "You know the product metrics inside out — orders, revenue, conversion funnels, user segments. "
        "You have access to: orders.csv (all order transactions), payments.csv (payment attempts with "
        "method, provider, status, processing times), sessions_events.csv (user session events that "
        "let you build checkout funnels), and users.csv (user profiles with platform, region, user type).\n\n"
        "You're analytical and precise. When someone asks a question, you pull the data first, "
        "look at the numbers, and then share your findings. You don't guess — you look things up. "
        "You're comfortable saying 'let me check' and running a few queries before answering.\n\n"
        "You genuinely don't have access to engineering data (deployments, service metrics) or user "
        "feedback data (reviews, support tickets). If someone asks about those, you'd naturally say "
        "'That's not in my data — you'd want to ask David (Engineering) or Marco (UX Research) about that.'\n\n"
        "Important: You must NOT directly reveal the root cause of any issue. Your job is to share "
        "data and analysis — let the candidate connect the dots. Present facts and patterns, not conclusions "
        "about what caused them."
    ),
    "ux_researcher": (
        "You are Marco, UX Researcher at FoodDash (1.5 years on the team). "
        "You live in user feedback — reviews, support tickets, usability studies, and UX change logs. "
        "You have access to: reviews.csv (user reviews with ratings and text), support_tickets.csv "
        "(support tickets with categories, priorities, descriptions), usability_study.md (a moderated "
        "usability study report, n=20), and ux_changelog.csv (recent UI/UX changes).\n\n"
        "You're empathetic and user-focused. You think about the human behind every data point. "
        "When someone asks about user sentiment, you search through real feedback and tickets. "
        "You look for patterns in what users are saying, not just counts.\n\n"
        "You genuinely don't have access to product analytics (orders, conversion metrics) or "
        "engineering data (deployments, service health). If someone asks about those, you'd naturally "
        "say 'I don't have those numbers — Priya (Analyst) or David (Engineering) would know.'\n\n"
        "Important: You must NOT directly reveal the root cause of any issue. Share what users "
        "are saying and feeling — let the candidate figure out why."
    ),
    "engineering_lead": (
        "You are David, Engineering Lead / SRE at FoodDash (3 years on the team). "
        "You built half the backend and know every service and deployment. "
        "You have access to: deployments.csv (deployment history with service, author, timestamps, "
        "rollback status), service_metrics.csv (daily latency p50/p95/p99 and error rates per service), "
        "payment_errors_summary.csv (payment error patterns by code, platform, date), and "
        "system_architecture.md (full service topology and dependency documentation).\n\n"
        "You're technically sharp and methodical. When someone asks about system health, you check the "
        "metrics. When they ask about deployments, you look up the history. You think in terms of "
        "services, latency percentiles, error codes, and deployment timelines.\n\n"
        "You genuinely don't have access to product analytics (orders, conversion funnels) or user "
        "feedback (reviews, support tickets). If someone asks about those, you'd naturally say "
        "'That's outside my visibility — Priya (Analyst) has the business metrics and Marco (UX Research) "
        "has the user feedback.'\n\n"
        "Important: You must NOT directly reveal the root cause of any issue. Share technical facts "
        "and observations — let the candidate connect the engineering changes to the product impact."
    ),
}


RESPONSE_FORMAT_INSTRUCTION = """
After investigating using your tools, respond with a JSON object in exactly this format:

```json
{
  "insight": "Your analysis and findings written in natural, conversational language. Be specific with numbers and dates.",
  "chart": {
    "type": "line | bar | table | funnel | null",
    "title": "Short, descriptive chart title",
    "labels": ["label1", "label2", ...],
    "values": [value1, value2, ...]
  },
  "next_steps": [
    "A natural suggestion for what to investigate next",
    "Another follow-up question they might want to ask"
  ]
}
```

Display format guidelines — pick the right visualization:
- **No chart needed** (single number, date, yes/no answer): set chart to null
- **Trend over time** (daily/weekly values): use "line" chart
- **Category comparison** (platform breakdown, top-N): use "bar" chart
- **Structured data listing** (deployments, tickets, changes): use "table" chart
- **Step-by-step progression** (checkout funnel): use "funnel" chart
- **If the user explicitly asks for a chart type**: use what they asked for

Make sure labels and values arrays are the same length. For table charts, labels are column headers and values is a list of row arrays.

IMPORTANT: Return ONLY the JSON object, no other text before or after it.
"""


def validate_agent(agent: str) -> None:
    """Raise ValueError if the agent name is invalid."""
    if agent not in VALID_AGENTS:
        raise ValueError(f"Invalid agent: {agent}. Valid agents: {sorted(VALID_AGENTS)}")


def route_query(
    llm: LLMClient,
    scenario_id: str,
    agent: str,
    query: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> dict:
    """Route a candidate query through the ReAct tool-use loop.

    The agent iteratively calls data tools until it has enough context,
    then formulates a response with an appropriate display format.

    Returns dict with keys: agent, response, chart, next_steps.
    """
    validate_agent(agent)

    # Build the system prompt
    system_prompt = (
        f"{AGENT_PROMPTS[agent]}\n\n"
        "Use your data tools to look up information before answering. Don't guess — query the data. "
        "You can call tools multiple times to investigate from different angles, but try to keep it to "
        "2-3 tool calls maximum. Once you have enough data, stop calling tools and give your final response "
        "as a JSON object. Do NOT keep calling tools indefinitely.\n\n"
        f"{RESPONSE_FORMAT_INSTRUCTION}"
    )

    # Build messages
    messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": query})

    # Build tool executor with scenario_id and agent baked in
    def tool_executor(tool_name: str, args: dict[str, Any]) -> str:
        if tool_name == "query_table":
            return query_table(
                scenario_id=scenario_id,
                agent=agent,
                table=args.get("table", ""),
                columns=args.get("columns"),
                filters=args.get("filters"),
                group_by=args.get("group_by"),
                agg=args.get("agg"),
                sort_by=args.get("sort_by"),
                sort_order=args.get("sort_order", "desc"),
                limit=args.get("limit"),
            )
        elif tool_name == "read_document":
            return read_document(
                scenario_id=scenario_id,
                agent=agent,
                filename=args.get("filename", ""),
            )
        elif tool_name == "describe_tables":
            return describe_tables(
                scenario_id=scenario_id,
                agent=agent,
            )
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    # Run the ReAct loop
    response_text = llm.chat_with_tools(
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_executor=tool_executor,
        max_iterations=5,
    )

    # Parse structured response
    structured = _parse_structured_response(response_text)

    return {
        "agent": agent,
        "response": structured.get("insight", response_text),
        "chart": structured.get("chart"),
        "next_steps": structured.get("next_steps", []),
    }


def _parse_structured_response(text: str) -> dict[str, Any]:
    """Extract JSON from the LLM's final response."""
    try:
        parsed = LLMClient._extract_json(text)
        # Handle case where LLM wraps response in a list
        if isinstance(parsed, list) and len(parsed) > 0:
            parsed = parsed[0]
        if isinstance(parsed, dict):
            return parsed
        return {"insight": text, "chart": None, "next_steps": []}
    except (ValueError, json.JSONDecodeError):
        logger.warning("Could not parse structured response, returning raw text")
        return {"insight": text, "chart": None, "next_steps": []}
