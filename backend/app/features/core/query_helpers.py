"""
Utility for building parameterized partial-update SQL queries.

SECURITY NOTE: `table` and column names are string-interpolated into SQL.
This is safe ONLY because they come from hardcoded developer code (service
functions), never from user input. Never pass user-supplied values as `table`
or as keys in `where`/`updates`.
"""
import json
from typing import Any


def build_partial_update_query(
    table: str,
    where: dict[str, Any],
    updates: dict[str, Any],
    jsonb_fields: set[str] | None = None,
    returning: str = "*",
) -> tuple[str, list[Any]]:
    """Build a parameterized UPDATE SQL query from a dict of changed fields.

    Args:
        table: Table name (developer-controlled, never user input).
        where: Dict of column->value pairs for the WHERE clause.
        updates: Dict of column->value pairs for the SET clause (only fields to update).
        jsonb_fields: Set of column names that need ::jsonb casting.
        returning: RETURNING clause (default "*").

    Returns:
        (sql_string, params_list) where params_list values correspond to $1, $2, ...

    Raises:
        ValueError: If updates dict is empty.
    """
    if not updates:
        raise ValueError("No fields to update")

    jsonb_fields = jsonb_fields or set()
    params = []
    set_parts = []

    # Build SET clause - update fields first
    for col, val in updates.items():
        params.append(json.dumps(val) if col in jsonb_fields else val)
        n = len(params)
        cast = "::jsonb" if col in jsonb_fields else ""
        set_parts.append(f"{col}=${n}{cast}")

    # Always add updated_at=NOW() (non-parameterized)
    set_parts.append("updated_at=NOW()")

    # Build WHERE clause - continuing $N sequence
    where_parts = []
    for col, val in where.items():
        params.append(val)
        n = len(params)
        where_parts.append(f"{col}=${n}")

    sql = (
        f"UPDATE {table} SET {', '.join(set_parts)} "
        f"WHERE {' AND '.join(where_parts)} "
        f"RETURNING {returning}"
    )
    return sql, params
