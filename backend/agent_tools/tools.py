"""Generic data tools for agentic agents.

Three primitives that replace all rigid skill functions:
  - query_table: flexible CSV querying with filters, group_by, aggregation
  - read_document: returns markdown/text file contents
  - describe_tables: schema info for all accessible tables

Each tool validates that the agent has access to the requested table
via AGENT_TABLE_ACCESS before operating.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from telemetry_layer.telemetry import AGENT_TABLE_ACCESS

logger = logging.getLogger(__name__)

SCENARIOS_DIR = Path(__file__).resolve().parent.parent.parent / "scenarios"

MAX_RESULT_ROWS = 50


# ────────────────────────────────────────────────────
# Access control
# ────────────────────────────────────────────────────


def _validate_access(agent: str, table: str) -> None:
    """Raise if the agent is not allowed to access this table."""
    allowed = AGENT_TABLE_ACCESS.get(agent, [])
    if table not in allowed:
        raise PermissionError(
            f"Agent '{agent}' does not have access to '{table}'. "
            f"Accessible tables: {allowed}"
        )


def _table_path(scenario_id: str, filename: str) -> Path:
    return SCENARIOS_DIR / scenario_id / "tables" / filename


# ────────────────────────────────────────────────────
# Tool 1: query_table
# ────────────────────────────────────────────────────


def query_table(
    scenario_id: str,
    agent: str,
    table: str,
    columns: list[str] | None = None,
    filters: dict[str, Any] | None = None,
    group_by: str | None = None,
    agg: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "desc",
    limit: int | None = None,
) -> str:
    """Query a CSV table with optional filters, grouping, aggregation, sorting.

    Args:
        table: CSV filename (e.g. "orders.csv")
        columns: Optional list of columns to return
        filters: Dict of column_name -> value or operator conditions:
                 {"platform": "ios"} — exact match
                 {"error_rate_pct >": 1.0} — comparison (supports >, <, >=, <=, !=)
                 {"text contains": "payment"} — substring search (case-insensitive)
        group_by: Column to group by
        agg: Aggregation function: count, sum, mean, min, max, count_unique, or
             column-specific like "sum:total_amount" or "mean:processing_time_ms"
        sort_by: Column to sort by
        sort_order: "asc" or "desc" (default "desc")
        limit: Max rows to return

    Returns:
        JSON string with query results.
    """
    _validate_access(agent, table)

    path = _table_path(scenario_id, table)
    if not path.exists():
        return json.dumps({"error": f"Table not found: {table}"})

    df = pd.read_csv(path)

    # Apply filters
    if filters:
        for key, value in filters.items():
            parts = key.strip().rsplit(" ", 1)
            if len(parts) == 2 and parts[1] in (">", "<", ">=", "<=", "!="):
                col, op = parts
                col = col.strip()
                if col not in df.columns:
                    continue
                if op == ">":
                    df = df[df[col] > value]
                elif op == "<":
                    df = df[df[col] < value]
                elif op == ">=":
                    df = df[df[col] >= value]
                elif op == "<=":
                    df = df[df[col] <= value]
                elif op == "!=":
                    df = df[df[col] != value]
            elif len(parts) == 2 and parts[1].lower() == "contains":
                col = parts[0].strip()
                if col in df.columns:
                    df = df[df[col].astype(str).str.contains(str(value), case=False, na=False)]
            else:
                # Exact match
                col = key.strip()
                if col in df.columns:
                    df = df[df[col] == value]

    # Select columns (before grouping, to validate)
    if columns and not group_by:
        valid_cols = [c for c in columns if c in df.columns]
        if valid_cols:
            df = df[valid_cols]

    # Group by + aggregate
    if group_by and group_by in df.columns:
        agg_fn = agg or "count"

        # Parse column-specific aggregation: "sum:total_amount"
        if ":" in agg_fn:
            fn_name, agg_col = agg_fn.split(":", 1)
            if agg_col in df.columns:
                if fn_name == "count_unique":
                    grouped = df.groupby(group_by)[agg_col].nunique().reset_index()
                    grouped.columns = [group_by, f"{agg_col}_unique_count"]
                else:
                    grouped = df.groupby(group_by)[agg_col].agg(fn_name).reset_index()
                    grouped.columns = [group_by, f"{agg_col}_{fn_name}"]
            else:
                grouped = df.groupby(group_by).size().reset_index(name="count")
        elif agg_fn == "count":
            grouped = df.groupby(group_by).size().reset_index(name="count")
        elif agg_fn == "count_unique":
            # Count unique across all columns — pick the first non-group column
            other_cols = [c for c in df.columns if c != group_by]
            if other_cols:
                grouped = df.groupby(group_by)[other_cols[0]].nunique().reset_index()
                grouped.columns = [group_by, f"{other_cols[0]}_unique_count"]
            else:
                grouped = df.groupby(group_by).size().reset_index(name="count")
        else:
            # Apply agg to all numeric columns
            numeric_df = df.select_dtypes(include="number")
            if not numeric_df.empty:
                numeric_df[group_by] = df[group_by]
                grouped = numeric_df.groupby(group_by).agg(agg_fn).reset_index()
            else:
                grouped = df.groupby(group_by).size().reset_index(name="count")

        df = grouped

    # Sort
    if sort_by and sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=(sort_order == "asc"))
    elif group_by and len(df.columns) >= 2:
        # Default: sort by the aggregated value column descending
        val_col = [c for c in df.columns if c != group_by]
        if val_col:
            df = df.sort_values(val_col[0], ascending=False)

    # Limit
    total_rows = len(df)
    effective_limit = min(limit or MAX_RESULT_ROWS, MAX_RESULT_ROWS)
    df = df.head(effective_limit)

    result = {
        "table": table,
        "total_matching_rows": total_rows,
        "returned_rows": len(df),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records"),
    }
    if total_rows > effective_limit:
        result["note"] = f"Showing top {effective_limit} of {total_rows} rows. Refine filters for more specific results."

    return json.dumps(result, default=str)


# ────────────────────────────────────────────────────
# Tool 2: read_document
# ────────────────────────────────────────────────────


def read_document(scenario_id: str, agent: str, filename: str) -> str:
    """Read a markdown or text file from the scenario tables directory.

    Returns the full content of the file.
    """
    _validate_access(agent, filename)

    path = _table_path(scenario_id, filename)
    if not path.exists():
        return json.dumps({"error": f"Document not found: {filename}"})

    content = path.read_text()
    return json.dumps({"filename": filename, "content": content})


# ────────────────────────────────────────────────────
# Tool 3: describe_tables
# ────────────────────────────────────────────────────


def describe_tables(scenario_id: str, agent: str) -> str:
    """List all accessible tables with schema info.

    For each table: name, columns (name + dtype), row count, and a sample row.
    """
    allowed = AGENT_TABLE_ACCESS.get(agent, [])
    tables_info = []

    for filename in allowed:
        path = _table_path(scenario_id, filename)
        if not path.exists():
            tables_info.append({"name": filename, "status": "not_found"})
            continue

        if filename.endswith(".csv"):
            df = pd.read_csv(path)
            col_info = [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns]
            sample = df.head(2).to_dict(orient="records")

            # Date range detection
            date_cols = [c for c in df.columns if any(kw in c.lower() for kw in ("date", "timestamp", "created_at", "_at"))]
            date_range = None
            if date_cols:
                dc = date_cols[0]
                try:
                    dates = pd.to_datetime(df[dc])
                    date_range = {"column": dc, "min": str(dates.min()), "max": str(dates.max())}
                except Exception:
                    pass

            info: dict[str, Any] = {
                "name": filename,
                "type": "csv",
                "rows": len(df),
                "columns": col_info,
                "sample": sample,
            }
            if date_range:
                info["date_range"] = date_range
            tables_info.append(info)

        elif filename.endswith(".md"):
            content = path.read_text()
            tables_info.append({
                "name": filename,
                "type": "markdown",
                "size_chars": len(content),
                "preview": content[:300] + ("..." if len(content) > 300 else ""),
            })
        else:
            tables_info.append({"name": filename, "type": "unknown"})

    return json.dumps({"agent": agent, "accessible_tables": tables_info}, default=str)


# ────────────────────────────────────────────────────
# Tool definitions (OpenAI function-calling format)
# ────────────────────────────────────────────────────

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "query_table",
            "description": (
                "Query a CSV table with optional filtering, grouping, and aggregation. "
                "Use this for any data analysis: trends, breakdowns, comparisons, counts, etc. "
                "You can call this multiple times to investigate from different angles."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "CSV filename to query (e.g. 'orders.csv', 'payments.csv')",
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of columns to return. Omit to return all.",
                    },
                    "filters": {
                        "type": "object",
                        "description": (
                            "Optional filters. Keys are 'column_name' for exact match, "
                            "'column_name >' for comparison, or 'column_name contains' for substring search. "
                            "Examples: {\"platform\": \"ios\"}, {\"error_rate_pct >\": 1.0}, {\"text contains\": \"payment\"}"
                        ),
                    },
                    "group_by": {
                        "type": "string",
                        "description": "Column to group results by.",
                    },
                    "agg": {
                        "type": "string",
                        "description": (
                            "Aggregation: 'count', 'sum', 'mean', 'min', 'max', 'count_unique', "
                            "or column-specific like 'sum:total_amount', 'mean:processing_time_ms', 'count_unique:user_id'."
                        ),
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Column to sort results by.",
                    },
                    "sort_order": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "description": "Sort direction. Default: 'desc'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max rows to return (capped at 50).",
                    },
                },
                "required": ["table"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_document",
            "description": (
                "Read a markdown or text document from the data sources. "
                "Use this for qualitative data like architecture docs, usability studies, or changelogs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The document filename (e.g. 'system_architecture.md', 'usability_study.md')",
                    },
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_tables",
            "description": (
                "List all data tables you have access to, with column names, data types, row counts, "
                "date ranges, and sample rows. Call this when you need to understand what data is available "
                "or when someone asks about your data sources."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]
