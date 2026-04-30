"""Integration tests for research endpoints."""
import uuid
import pytest


def _create_profile(client):
    resp = client.post("/profile")
    assert resp.status_code == 201
    return resp.json()


def _research_payload(**overrides):
    base = {
        "paper_name": "Attention Is All You Need",
        "publication_link": "https://arxiv.org/abs/1706.03762",
        "description": "Transformer architecture paper.",
    }
    base.update(overrides)
    return base


def test_list_researches_empty(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    resp = client.get("/profile/research")
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_and_list_research(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    post_resp = client.post("/profile/research", json=_research_payload())
    assert post_resp.status_code == 201
    resp = client.get("/profile/research")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["paper_name"] == "Attention Is All You Need"


def test_get_research_by_id(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/research", json=_research_payload()).json()
    resp = client.get(f"/profile/research/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_update_research(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/research", json=_research_payload()).json()
    updated_payload = _research_payload(paper_name="BERT: Pre-training of Deep Bidirectional Transformers")
    resp = client.patch(f"/profile/research/{created['id']}", json=updated_payload)
    assert resp.status_code == 200
    assert resp.json()["paper_name"] == "BERT: Pre-training of Deep Bidirectional Transformers"


def test_delete_research(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/research", json=_research_payload()).json()
    resp = client.delete(f"/profile/research/{created['id']}")
    assert resp.status_code == 204
    # Verify it's gone
    resp2 = client.get(f"/profile/research/{created['id']}")
    assert resp2.status_code == 404


def test_description_is_optional(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _research_payload()
    del payload["description"]
    resp = client.post("/profile/research", json=payload)
    assert resp.status_code == 201
    assert resp.json()["description"] is None


def test_delete_other_users_research_returns_404(app):
    """Deleting another user's research entry returns 404 (not 403)."""
    import asyncio, asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password
    from fastapi.testclient import TestClient

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(conn, email=f"research-{uuid.uuid4().hex}@example.com", password_hash=hash_password("x"))
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    # User A creates a profile and adds a research entry
    async def override_a(): return user_a
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        research = ca.post("/profile/research", json=_research_payload()).json()

    # User B tries to delete User A's research entry
    async def override_b(): return user_b
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        # User B has no profile, so get_profile_or_404 returns 404
        resp = cb.delete(f"/profile/research/{research['id']}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_html_in_paper_name_stripped(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _research_payload(paper_name="<b>Attention</b> Is All You Need")
    resp = client.post("/profile/research", json=payload)
    assert resp.status_code == 201
    assert resp.json()["paper_name"] == "Attention Is All You Need"


def test_unauthenticated_returns_401(client):
    resp = client.get("/profile/research")
    assert resp.status_code == 401


def test_create_research_with_journal_year(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    payload = _research_payload(journal="Nature", year="2024")
    resp = client.post("/profile/research", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["journal"] == "Nature"
    assert data["year"] == "2024"


def test_update_research_journal(authenticated_client):
    client, _ = authenticated_client
    _create_profile(client)
    created = client.post("/profile/research", json=_research_payload(journal="Nature", year="2023")).json()
    assert created["journal"] == "Nature"
    updated_payload = _research_payload(journal="Science", year="2024")
    resp = client.patch(f"/profile/research/{created['id']}", json=updated_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["journal"] == "Science"
    assert data["year"] == "2024"
