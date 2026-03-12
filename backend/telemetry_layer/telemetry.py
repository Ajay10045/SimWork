"""Telemetry data layer — enforces domain access rules.

Each agent role has access to a specific set of tables under
scenarios/<scenario_id>/tables/. This module defines those access rules.
"""

from __future__ import annotations


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

VALID_AGENTS = set(AGENT_TABLE_ACCESS.keys())
