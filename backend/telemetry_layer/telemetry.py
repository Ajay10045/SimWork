"""Telemetry data layer — enforces domain access rules.

Each agent role has access to a specific set of tables under
scenarios/<scenario_id>/tables/. This module enforces those access rules.
"""

from __future__ import annotations

from typing import Any

from scenario_loader.loader import load_tables, load_telemetry

# Which table files each agent role can access
AGENT_TABLE_ACCESS: dict[str, list[str]] = {
    "analyst": [
        "orders.csv",
        "payments.csv",
        "sessions_events.csv",
        "users.csv",
    ],
    "ux_researcher": [
        "reviews.csv",
        "support_tickets.csv",
        "usability_study.md",
        "ux_changelog.csv",
    ],
    "engineering_lead": [
        "deployments.csv",
        "service_metrics.csv",
        "system_architecture.md",
        "payment_errors_summary.csv",
    ],
}

# Legacy domain mapping (kept for backward compatibility with old data layout)
AGENT_DOMAIN_MAP: dict[str, str] = {
    "analyst": "analytics",
    "ux_researcher": "user_signals",
    "engineering_lead": "observability",
}

VALID_AGENTS = set(AGENT_TABLE_ACCESS.keys())


def get_domain_for_agent(agent: str) -> str:
    """Return the telemetry domain an agent is allowed to access."""
    if agent not in AGENT_DOMAIN_MAP:
        raise ValueError(f"Invalid agent: {agent}. Valid agents: {list(AGENT_DOMAIN_MAP.keys())}")
    return AGENT_DOMAIN_MAP[agent]


def get_telemetry_for_agent(scenario_id: str, agent: str) -> dict[str, Any]:
    """Load telemetry data scoped to the agent's allowed tables.

    Tries the new tables/ directory first (with per-agent file filtering).
    Falls back to the legacy domain-directory layout.
    """
    if agent not in AGENT_TABLE_ACCESS:
        raise ValueError(f"Invalid agent: {agent}. Valid agents: {sorted(VALID_AGENTS)}")

    allowed_files = AGENT_TABLE_ACCESS[agent]

    try:
        return load_tables(scenario_id, allowed_files)
    except FileNotFoundError:
        # Fall back to legacy domain directories
        domain = get_domain_for_agent(agent)
        return load_telemetry(scenario_id, domain)


def get_raw_table(scenario_id: str, filename: str) -> Any:
    """Load a single raw table file from the scenario's tables/ directory.

    Returns DataFrame records (list[dict]) for CSV, raw text for markdown,
    parsed dict for JSON.
    """
    result = load_tables(scenario_id, [filename])
    if filename not in result:
        raise FileNotFoundError(f"Table not found: {filename}")
    return result[filename]


def format_telemetry_context(telemetry_data: dict[str, Any]) -> str:
    """Format telemetry data into a text context string for the LLM."""
    parts: list[str] = []
    for filename, content in telemetry_data.items():
        parts.append(f"--- {filename} ---")
        if isinstance(content, list):
            # CSV records
            for row in content:
                parts.append(str(row))
        elif isinstance(content, str):
            # Markdown content
            parts.append(content)
        elif isinstance(content, dict):
            import json

            parts.append(json.dumps(content, indent=2))
        else:
            parts.append(str(content))
        parts.append("")
    return "\n".join(parts)
