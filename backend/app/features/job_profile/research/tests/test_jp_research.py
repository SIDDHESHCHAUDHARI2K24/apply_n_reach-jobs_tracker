"""Integration tests for job profile research endpoints."""
import uuid
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.features.job_profile.tests.conftest import _create_job_profile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _research_payload(**overrides):
    base = {
        "paper_name": "ML Paper",
        "publication_link": "https://arxiv.org/abs/1234",
        "description": "Research on ML",
    }
    base.update(overrides)
    return base


def _create_research(client, jp_id, **overrides):
    resp = client.post(f"/job-profiles/{jp_id}/research", json=_research_payload(**overrides))
    assert resp.status_code == 201, f"Failed to create research: {resp.status_code} {resp.text}"
    return resp.json()


def _create_master_research(client):
    resp = client.post("/profile/research", json={
        "paper_name": "ML Paper",
        "publication_link": "https://arxiv.org/abs/1234",
        "description": "Research on ML",
    })
    assert resp.status_code == 201, f"Failed to create master research: {resp.status_code} {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_list_empty(authenticated_client):
    """1. Listing research on a new job profile returns an empty list."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    resp = client.get(f"/job-profiles/{jp['id']}/research")
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_and_list(authenticated_client):
    """2. Adding a research entry and then listing returns it."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    _create_research(client, jp["id"])
    resp = client.get(f"/job-profiles/{jp['id']}/research")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["paper_name"] == "ML Paper"
    assert data[0]["publication_link"] == "https://arxiv.org/abs/1234"
    assert data[0]["description"] == "Research on ML"
    assert data[0]["job_profile_id"] == jp["id"]


def test_get_by_id(authenticated_client):
    """3. Fetching a research entry by ID returns the correct item."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_research(client, jp["id"])
    resp = client.get(f"/job-profiles/{jp['id']}/research/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]
    assert resp.json()["paper_name"] == "ML Paper"


def test_update_single_field(authenticated_client):
    """4. PATCH with only paper_name updates just that field."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_research(client, jp["id"])
    resp = client.patch(
        f"/job-profiles/{jp['id']}/research/{created['id']}",
        json={"paper_name": "Updated Paper"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["paper_name"] == "Updated Paper"
    # Other fields unchanged
    assert data["publication_link"] == created["publication_link"]
    assert data["description"] == created["description"]


def test_delete(authenticated_client):
    """5. Deleting a research entry returns 204 and it's gone."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_research(client, jp["id"])
    resp = client.delete(f"/job-profiles/{jp['id']}/research/{created['id']}")
    assert resp.status_code == 204
    resp2 = client.get(f"/job-profiles/{jp['id']}/research/{created['id']}")
    assert resp2.status_code == 404


def test_partial_update_empty_body_400(authenticated_client):
    """6. PATCH with an empty body returns 400."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_research(client, jp["id"])
    resp = client.patch(
        f"/job-profiles/{jp['id']}/research/{created['id']}",
        json={},
    )
    assert resp.status_code == 400


def test_html_stripped(authenticated_client):
    """7. HTML tags in paper_name are stripped by sanitize_text."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    resp = client.post(
        f"/job-profiles/{jp['id']}/research",
        json=_research_payload(paper_name="<b>Awesome</b> Paper"),
    )
    assert resp.status_code == 201
    assert resp.json()["paper_name"] == "Awesome Paper"


def test_cross_user_returns_404(app):
    """8. Accessing another user's job profile research returns 404."""
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(
                conn,
                email=f"jp-research-cross-{uuid.uuid4().hex}@example.com",
                password_hash=hash_password("x"),
            )
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    async def override_a():
        return user_a

    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        jp = ca.post("/job-profiles", json={
            "profile_name": f"Cross Test {uuid.uuid4().hex[:6]}",
            "target_role": "SWE",
            "target_company": "Corp",
        }).json()
        entry = ca.post(f"/job-profiles/{jp['id']}/research", json=_research_payload()).json()

    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        resp = cb.get(f"/job-profiles/{jp['id']}/research/{entry['id']}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_unauthenticated_401(client):
    """9. Unauthenticated requests to research endpoint return 401."""
    resp = client.get("/job-profiles/1/research")
    assert resp.status_code == 401


def test_source_research_id_null(authenticated_client):
    """10. Manually added research entries have source_research_id=null."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_research(client, jp["id"])
    assert created["source_research_id"] is None


def test_import_success(authenticated_client):
    """11. Importing a master research entry succeeds."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    master = _create_master_research(client)
    resp = client.post(
        f"/job-profiles/{jp['id']}/research/import",
        json={"source_ids": [master["id"]]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert master["id"] in data["imported"]
    assert data["skipped"] == []
    assert data["not_found"] == []

    # Verify the entry was created with correct source_research_id
    list_resp = client.get(f"/job-profiles/{jp['id']}/research")
    assert list_resp.status_code == 200
    entries = list_resp.json()
    assert len(entries) == 1
    assert entries[0]["source_research_id"] == master["id"]
    assert entries[0]["paper_name"] == master["paper_name"]


def test_import_skips_duplicates(authenticated_client):
    """12. Importing the same research entry twice skips the second import."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    master = _create_master_research(client)

    # First import
    client.post(
        f"/job-profiles/{jp['id']}/research/import",
        json={"source_ids": [master["id"]]},
    )

    # Second import — should skip
    resp = client.post(
        f"/job-profiles/{jp['id']}/research/import",
        json={"source_ids": [master["id"]]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == []
    assert master["id"] in data["skipped"]

    # Only one entry total
    list_resp = client.get(f"/job-profiles/{jp['id']}/research")
    assert len(list_resp.json()) == 1


def test_import_cross_user_not_found(app):
    """13. Importing another user's research returns not_found."""
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(
                conn,
                email=f"jp-research-import-cross-{uuid.uuid4().hex}@example.com",
                password_hash=hash_password("x"),
            )
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    # User A creates a master research entry
    async def override_a():
        return user_a

    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        master = ca.post("/profile/research", json={
            "paper_name": "Private Paper",
            "publication_link": "https://example.com",
            "description": "Private research",
        }).json()

    # User B tries to import User A's research into their own job profile
    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        cb.post("/profile")
        jp = cb.post("/job-profiles", json={
            "profile_name": f"B Profile {uuid.uuid4().hex[:6]}",
            "target_role": "SWE",
            "target_company": "Corp",
        }).json()
        resp = cb.post(
            f"/job-profiles/{jp['id']}/research/import",
            json={"source_ids": [master["id"]]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert master["id"] in data["not_found"]
        assert data["imported"] == []

    app.dependency_overrides.clear()


def test_import_empty_ids_422(authenticated_client):
    """14. Importing with empty source_ids list returns 422."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    resp = client.post(
        f"/job-profiles/{jp['id']}/research/import",
        json={"source_ids": []},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# B5 parity tests: journal and year fields
# ---------------------------------------------------------------------------

def test_journal_field_roundtrip(authenticated_client):
    """B5: journal is stored and returned correctly."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    resp = client.post(
        f"/job-profiles/{jp['id']}/research",
        json=_research_payload(journal="Nature", year="2023"),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["journal"] == "Nature"
    assert data["year"] == "2023"


def test_year_field_roundtrip(authenticated_client):
    """B5: year is stored and returned correctly on its own."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    resp = client.post(
        f"/job-profiles/{jp['id']}/research",
        json=_research_payload(year="2024"),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["year"] == "2024"
    assert data["journal"] is None


def test_journal_year_default_null(authenticated_client):
    """B5: journal and year default to null when not provided."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_research(client, jp["id"])
    assert created["journal"] is None
    assert created["year"] is None


def test_journal_update(authenticated_client):
    """B5: PATCH updates journal correctly."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_research(client, jp["id"])
    resp = client.patch(
        f"/job-profiles/{jp['id']}/research/{created['id']}",
        json={"journal": "Science"},
    )
    assert resp.status_code == 200
    assert resp.json()["journal"] == "Science"
    assert resp.json()["paper_name"] == created["paper_name"]  # unchanged


def test_html_stripped_from_journal(authenticated_client):
    """B5: HTML tags in journal are stripped by sanitize_text."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    resp = client.post(
        f"/job-profiles/{jp['id']}/research",
        json=_research_payload(journal="<b>Nature</b>"),
    )
    assert resp.status_code == 201
    assert "<b>" not in resp.json()["journal"]
    assert "Nature" in resp.json()["journal"]


def test_delete_master_nullifies_source_id(authenticated_client):
    """15. Deleting the master research entry sets source_research_id to NULL."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    master = _create_master_research(client)

    # Import master research into job profile
    client.post(
        f"/job-profiles/{jp['id']}/research/import",
        json={"source_ids": [master["id"]]},
    )

    # Delete master research
    del_resp = client.delete(f"/profile/research/{master['id']}")
    assert del_resp.status_code == 204

    # Verify source_research_id is now NULL
    list_resp = client.get(f"/job-profiles/{jp['id']}/research")
    entries = list_resp.json()
    assert len(entries) == 1
    assert entries[0]["source_research_id"] is None
    assert entries[0]["paper_name"] == master["paper_name"]
