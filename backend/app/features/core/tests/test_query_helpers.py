"""
Unit tests for app.features.core.query_helpers.build_partial_update_query.

These are pure unit tests — no database connection required.
"""

import json
import pytest

from app.features.core.query_helpers import build_partial_update_query


class TestBuildPartialUpdateQuery:
    """Tests for build_partial_update_query."""

    # ------------------------------------------------------------------ #
    # Test 1 – Happy path: two update fields, two WHERE conditions         #
    # ------------------------------------------------------------------ #
    def test_happy_path_basic(self):
        sql, params = build_partial_update_query(
            table="educations",
            where={"id": 5, "profile_id": 3},
            updates={"major": "CS", "degree_type": "MS"},
        )

        assert sql.startswith("UPDATE educations SET"), (
            f"SQL should start with 'UPDATE educations SET', got: {sql!r}"
        )
        # SET clause params are $1, $2; WHERE params continue at $3, $4
        assert "WHERE" in sql
        assert "id=$3" in sql
        assert "profile_id=$4" in sql
        # updated_at must always be present, non-parameterized
        assert "updated_at=NOW()" in sql
        # Params: update values first, then where values
        assert params == ["CS", "MS", 5, 3]

    # ------------------------------------------------------------------ #
    # Test 2 – Empty updates dict → ValueError                            #
    # ------------------------------------------------------------------ #
    def test_empty_updates_raises_value_error(self):
        with pytest.raises(ValueError, match="No fields to update"):
            build_partial_update_query(
                table="educations",
                where={"id": 1},
                updates={},
            )

    # ------------------------------------------------------------------ #
    # Test 3 – Single update field                                        #
    # ------------------------------------------------------------------ #
    def test_single_update_field(self):
        sql, params = build_partial_update_query(
            table="projects",
            where={"id": 7},
            updates={"title": "New Title"},
        )

        assert "UPDATE projects SET" in sql
        assert "title=$1" in sql
        assert "updated_at=NOW()" in sql
        assert "WHERE" in sql
        assert "id=$2" in sql
        assert params == ["New Title", 7]

    # ------------------------------------------------------------------ #
    # Test 4 – JSONB field: cast and json.dumps in params                 #
    # ------------------------------------------------------------------ #
    def test_jsonb_field_gets_cast_and_json_dumps(self):
        bullet_points = ["Led a team", "Shipped feature X"]
        sql, params = build_partial_update_query(
            table="experiences",
            where={"id": 10, "profile_id": 2},
            updates={"title": "Engineer", "bullet_points": bullet_points},
            jsonb_fields={"bullet_points"},
        )

        # JSONB field must have ::jsonb cast in SQL
        assert "bullet_points=$2::jsonb" in sql or "bullet_points=$1::jsonb" in sql, (
            f"Expected '::jsonb' cast for bullet_points in SQL: {sql!r}"
        )
        # The param value for bullet_points must be json.dumps'd
        assert json.dumps(bullet_points) in params, (
            "Expected json.dumps(bullet_points) in params"
        )
        # Non-JSONB field must NOT have ::jsonb cast
        assert "title=$1::jsonb" not in sql
        assert "title=$2::jsonb" not in sql

    # ------------------------------------------------------------------ #
    # Test 5 – updated_at=NOW() is always in SET, never parameterized     #
    # ------------------------------------------------------------------ #
    def test_updated_at_always_present_and_not_parameterized(self):
        sql, params = build_partial_update_query(
            table="certifications",
            where={"id": 99},
            updates={"name": "AWS SAA"},
        )

        assert "updated_at=NOW()" in sql
        # Make sure updated_at doesn't appear as a $N param placeholder pair
        # i.e., there's no "updated_at=$" pattern
        assert "updated_at=$" not in sql

    # ------------------------------------------------------------------ #
    # Test 6 – RETURNING clause included                                  #
    # ------------------------------------------------------------------ #
    def test_returning_clause_default(self):
        sql, _ = build_partial_update_query(
            table="educations",
            where={"id": 1},
            updates={"major": "Biology"},
        )
        assert "RETURNING *" in sql

    def test_returning_clause_custom(self):
        sql, _ = build_partial_update_query(
            table="educations",
            where={"id": 1},
            updates={"major": "Biology"},
            returning="id, major",
        )
        assert "RETURNING id, major" in sql

    # ------------------------------------------------------------------ #
    # Test 7 – WHERE clause with single condition                         #
    # ------------------------------------------------------------------ #
    def test_where_single_condition(self):
        sql, params = build_partial_update_query(
            table="skills",
            where={"profile_id": 42},
            updates={"skill_name": "Python"},
        )
        assert "WHERE profile_id=$2" in sql
        assert params == ["Python", 42]
