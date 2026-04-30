"""Integration tests for job profile experience CRUD and import endpoints."""
import uuid
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.features.auth.utils import get_current_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _exp_url(job_profile_id: int) -> str:
    return f"/job-profiles/{job_profile_id}/experience"


def _exp_item_url(job_profile_id: int, experience_id: int) -> str:
    return f"/job-profiles/{job_profile_id}/experience/{experience_id}"


def _create_experience(client, job_profile_id, **overrides):
    payload = {
        "role_title": "Software Engineer",
        "company_name": "Acme Corp",
        "start_month_year": "01/2020",
        "context": "Built things.",
        **overrides,
    }
    resp = client.post(_exp_url(job_profile_id), json=payload)
    assert resp.status_code == 201, f"Failed to create experience: {resp.status_code} {resp.text}"
    return resp.json()


def _create_master_experience(client, **overrides):
    payload = {
        "role_title": "Engineer",
        "company_name": "Google",
        "start_month_year": "07/2022",
        "context": "Backend work",
        **overrides,
    }
    resp = client.post("/profile/experience", json=payload)
    assert resp.status_code == 201, f"Failed to create master experience: {resp.status_code} {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD tests
# ---------------------------------------------------------------------------

def test_list_empty(authenticated_client):
    client, _, _, jp_id = authenticated_client
    resp = client.get(_exp_url(jp_id))
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_and_list(authenticated_client):
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(
        client, jp_id,
        work_sample_links=["https://example.com/sample"],
        bullet_points=["Designed REST APIs", "Led team of 5"],
    )
    assert exp["role_title"] == "Software Engineer"
    assert exp["company_name"] == "Acme Corp"
    assert exp["work_sample_links"] == ["https://example.com/sample"]
    assert exp["bullet_points"] == ["Designed REST APIs", "Led team of 5"]
    assert exp["job_profile_id"] == jp_id

    resp = client.get(_exp_url(jp_id))
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["id"] == exp["id"]


def test_get_by_id(authenticated_client):
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id)
    resp = client.get(_exp_item_url(jp_id, exp["id"]))
    assert resp.status_code == 200
    assert resp.json()["id"] == exp["id"]
    assert resp.json()["role_title"] == exp["role_title"]


def test_update_single_field(authenticated_client):
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id)
    resp = client.patch(_exp_item_url(jp_id, exp["id"]), json={"role_title": "Staff Engineer"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role_title"] == "Staff Engineer"
    assert data["company_name"] == exp["company_name"]  # unchanged


def test_delete(authenticated_client):
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id)
    resp = client.delete(_exp_item_url(jp_id, exp["id"]))
    assert resp.status_code == 204

    resp2 = client.get(_exp_item_url(jp_id, exp["id"]))
    assert resp2.status_code == 404


def test_partial_update_empty_body_400(authenticated_client):
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id)
    resp = client.patch(_exp_item_url(jp_id, exp["id"]), json={})
    assert resp.status_code == 400


def test_end_before_start_422(authenticated_client):
    client, _, _, jp_id = authenticated_client
    resp = client.post(_exp_url(jp_id), json={
        "role_title": "Engineer",
        "company_name": "Corp",
        "start_month_year": "07/2022",
        "end_month_year": "06/2022",
        "context": "Work",
    })
    assert resp.status_code == 422


def test_invalid_date_format_422(authenticated_client):
    client, _, _, jp_id = authenticated_client
    resp = client.post(_exp_url(jp_id), json={
        "role_title": "Engineer",
        "company_name": "Corp",
        "start_month_year": "2022-07",  # wrong format
        "context": "Work",
    })
    assert resp.status_code == 422


def test_html_stripped(authenticated_client):
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id, role_title="<b>Engineer</b>")
    assert "<b>" not in exp["role_title"]
    assert "Engineer" in exp["role_title"]


def test_cross_user_returns_404(app):
    """User B cannot access User A's job profile experiences."""
    from app.features.core.config import settings

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            from app.features.auth.models import ensure_auth_schema, create_user
            from app.features.auth.utils import hash_password
            await ensure_auth_schema(conn)
            email = f"jp-exp-cross-{uuid.uuid4().hex}@example.com"
            u = await create_user(conn, email=email, password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    async def override_a():
        return user_a

    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        jp_resp = ca.post("/job-profiles", json={
            "profile_name": f"UserA Resume {uuid.uuid4().hex[:8]}"
        })
        assert jp_resp.status_code == 201
        jp_id = jp_resp.json()["id"]
        exp = _create_experience(ca, jp_id)

    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        resp = cb.get(_exp_item_url(jp_id, exp["id"]))
        assert resp.status_code == 404

        resp2 = cb.delete(_exp_item_url(jp_id, exp["id"]))
        assert resp2.status_code == 404

    app.dependency_overrides.clear()


def test_unauthenticated_401(client):
    resp = client.get("/job-profiles/1/experience")
    assert resp.status_code == 401

    resp2 = client.post("/job-profiles/1/experience", json={
        "role_title": "Eng", "company_name": "Corp",
        "start_month_year": "01/2020", "context": "x"
    })
    assert resp2.status_code == 401


def test_source_experience_id_null_for_manual_entry(authenticated_client):
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id)
    assert exp["source_experience_id"] is None


def test_jsonb_fields_roundtrip(authenticated_client):
    client, _, _, jp_id = authenticated_client
    links = ["https://github.com/project"]
    bullets = ["Reduced latency by 40%", "Mentored 3 junior engineers"]
    exp = _create_experience(
        client, jp_id,
        work_sample_links=links,
        bullet_points=bullets,
    )

    resp = client.get(_exp_item_url(jp_id, exp["id"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["work_sample_links"] == links
    assert data["bullet_points"] == bullets


# ---------------------------------------------------------------------------
# B5 parity tests: max-1-link validator
# ---------------------------------------------------------------------------

def test_max_one_work_sample_link_create_422(authenticated_client):
    """B5: Creating an experience with 2+ work_sample_links returns 422."""
    client, _, _, jp_id = authenticated_client
    resp = client.post(_exp_url(jp_id), json={
        "role_title": "Engineer",
        "company_name": "Corp",
        "start_month_year": "01/2020",
        "context": "Work",
        "work_sample_links": ["https://example.com/a", "https://example.com/b"],
    })
    assert resp.status_code == 422


def test_max_one_work_sample_link_update_422(authenticated_client):
    """B5: Patching an experience with 2+ work_sample_links returns 422."""
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id)
    resp = client.patch(_exp_item_url(jp_id, exp["id"]), json={
        "work_sample_links": ["https://example.com/a", "https://example.com/b"],
    })
    assert resp.status_code == 422


def test_single_work_sample_link_accepted(authenticated_client):
    """B5: Creating an experience with exactly 1 work_sample_link is accepted."""
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id, work_sample_links=["https://example.com/demo"])
    assert exp["work_sample_links"] == ["https://example.com/demo"]


def test_empty_work_sample_links_accepted(authenticated_client):
    """B5: Creating an experience with an empty work_sample_links list is accepted."""
    client, _, _, jp_id = authenticated_client
    exp = _create_experience(client, jp_id, work_sample_links=[])
    assert exp["work_sample_links"] == []


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------

def test_import_success(authenticated_client):
    client, _, _, jp_id = authenticated_client
    master_exp = _create_master_experience(client)
    exp_id = master_exp["id"]

    resp = client.post(
        f"/job-profiles/{jp_id}/experience/import",
        json={"source_ids": [exp_id]},
    )
    assert resp.status_code == 200
    result = resp.json()
    assert exp_id in result["imported"]
    assert result["skipped"] == []
    assert result["not_found"] == []

    # Verify the imported entry exists and has the correct source_experience_id
    list_resp = client.get(_exp_url(jp_id))
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["source_experience_id"] == exp_id
    assert items[0]["role_title"] == master_exp["role_title"]


def test_import_skips_duplicates(authenticated_client):
    client, _, _, jp_id = authenticated_client
    master_exp = _create_master_experience(client)
    exp_id = master_exp["id"]

    # First import
    resp1 = client.post(
        f"/job-profiles/{jp_id}/experience/import",
        json={"source_ids": [exp_id]},
    )
    assert resp1.status_code == 200
    assert exp_id in resp1.json()["imported"]

    # Second import — should skip
    resp2 = client.post(
        f"/job-profiles/{jp_id}/experience/import",
        json={"source_ids": [exp_id]},
    )
    assert resp2.status_code == 200
    result = resp2.json()
    assert result["imported"] == []
    assert exp_id in result["skipped"]
    assert result["not_found"] == []


def test_import_cross_user_not_found(app):
    """User B's experience IDs are not found when user A tries to import them."""
    from app.features.core.config import settings

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            from app.features.auth.models import ensure_auth_schema, create_user
            from app.features.auth.utils import hash_password
            await ensure_auth_schema(conn)
            email = f"jp-exp-cross-import-{uuid.uuid4().hex}@example.com"
            u = await create_user(conn, email=email, password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    async def override_b():
        return user_b

    # User B creates their own master profile and experience
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        cb.post("/profile")
        b_exp = _create_master_experience(cb)
        b_exp_id = b_exp["id"]

    async def override_a():
        return user_a

    # User A tries to import user B's experience
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        jp_resp = ca.post("/job-profiles", json={
            "profile_name": f"User A Resume {uuid.uuid4().hex[:8]}"
        })
        assert jp_resp.status_code == 201
        jp_id = jp_resp.json()["id"]

        resp = ca.post(
            f"/job-profiles/{jp_id}/experience/import",
            json={"source_ids": [b_exp_id]},
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["imported"] == []
        assert result["skipped"] == []
        assert b_exp_id in result["not_found"]

    app.dependency_overrides.clear()


def test_import_empty_ids_422(authenticated_client):
    client, _, _, jp_id = authenticated_client
    resp = client.post(
        f"/job-profiles/{jp_id}/experience/import",
        json={"source_ids": []},
    )
    assert resp.status_code == 422


def test_delete_master_nullifies_source_id(authenticated_client):
    client, _, _, jp_id = authenticated_client
    master_exp = _create_master_experience(client)
    exp_id = master_exp["id"]

    # Import first
    import_resp = client.post(
        f"/job-profiles/{jp_id}/experience/import",
        json={"source_ids": [exp_id]},
    )
    assert import_resp.status_code == 200
    assert exp_id in import_resp.json()["imported"]

    # Verify source_experience_id is set
    list_resp = client.get(_exp_url(jp_id))
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["source_experience_id"] == exp_id
    jp_exp_id = items[0]["id"]

    # Delete the master experience
    del_resp = client.delete(f"/profile/experience/{exp_id}")
    assert del_resp.status_code == 204

    # The job profile experience should still exist, but source_experience_id should be null
    get_resp = client.get(_exp_item_url(jp_id, jp_exp_id))
    assert get_resp.status_code == 200
    assert get_resp.json()["source_experience_id"] is None
