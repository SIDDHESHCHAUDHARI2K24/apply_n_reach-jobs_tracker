"""Integration tests for job profile skills endpoints."""
import uuid
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.features.auth.utils import get_current_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skills_url(job_profile_id: int) -> str:
    return f"/job-profiles/{job_profile_id}/skills"


def _patch_skills(client, job_profile_id: int, skills: list) -> dict:
    return client.patch(_skills_url(job_profile_id), json={"skills": skills})


THREE_SKILLS = [
    {"kind": "technical", "name": "Python", "sort_order": 0},
    {"kind": "technical", "name": "FastAPI", "sort_order": 1},
    {"kind": "competency", "name": "Leadership", "sort_order": 0},
]


# ---------------------------------------------------------------------------
# Replace-all tests
# ---------------------------------------------------------------------------

def test_list_empty(authenticated_client):
    """Initially the skills list is empty."""
    client, _, _, job_profile_id = authenticated_client
    resp = client.get(_skills_url(job_profile_id))
    assert resp.status_code == 200
    assert resp.json() == []


def test_replace_skills(authenticated_client):
    """PATCH with 3 skills returns all 3."""
    client, _, _, job_profile_id = authenticated_client
    resp = _patch_skills(client, job_profile_id, THREE_SKILLS)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    names = {s["name"] for s in data}
    assert names == {"Python", "FastAPI", "Leadership"}


def test_replace_clears_existing(authenticated_client):
    """Second PATCH with 1 skill replaces the previous 3."""
    client, _, _, job_profile_id = authenticated_client
    _patch_skills(client, job_profile_id, THREE_SKILLS)
    resp = _patch_skills(client, job_profile_id, [
        {"kind": "technical", "name": "Go", "sort_order": 0},
    ])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Go"


def test_replace_empty_list_clears_all(authenticated_client):
    """PATCH with skills=[] clears all existing skills."""
    client, _, _, job_profile_id = authenticated_client
    _patch_skills(client, job_profile_id, THREE_SKILLS)
    resp = _patch_skills(client, job_profile_id, [])
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_skill_by_id(authenticated_client):
    """GET /skills/{id} returns the correct skill."""
    client, _, _, job_profile_id = authenticated_client
    _patch_skills(client, job_profile_id, [
        {"kind": "technical", "name": "Python", "sort_order": 0},
    ])
    skill_id = client.get(_skills_url(job_profile_id)).json()[0]["id"]
    resp = client.get(f"{_skills_url(job_profile_id)}/{skill_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Python"
    assert resp.json()["kind"] == "technical"


def test_get_nonexistent_skill_404(authenticated_client):
    """GET /skills/99999999 returns 404."""
    client, _, _, job_profile_id = authenticated_client
    resp = client.get(f"{_skills_url(job_profile_id)}/99999999")
    assert resp.status_code == 404


def test_invalid_kind_422(authenticated_client):
    """PATCH with kind='other' returns 422."""
    client, _, _, job_profile_id = authenticated_client
    resp = _patch_skills(client, job_profile_id, [
        {"kind": "other", "name": "Python", "sort_order": 0},
    ])
    assert resp.status_code == 422


def test_html_stripped_from_name(authenticated_client):
    """HTML tags are stripped from skill names via sanitize_text."""
    client, _, _, job_profile_id = authenticated_client
    resp = _patch_skills(client, job_profile_id, [
        {"kind": "technical", "name": "<b>Python</b>", "sort_order": 0},
    ])
    assert resp.status_code == 200
    assert resp.json()[0]["name"] == "Python"


def test_cross_user_returns_404(app):
    """GET on another user's job profile skills returns 404."""
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(
                conn,
                email=f"jp-skills-cross-{uuid.uuid4().hex}@example.com",
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
        jp_resp = ca.post("/job-profiles", json={
            "profile_name": f"Resume {uuid.uuid4().hex[:8]}",
            "target_role": "Engineer",
        })
        jp_id = jp_resp.json()["id"]

    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        resp = cb.get(_skills_url(jp_id))
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_unauthenticated_401(client):
    """Unauthenticated requests return 401."""
    resp = client.get("/job-profiles/1/skills")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Import tests (additive)
# ---------------------------------------------------------------------------

def _setup_master_skills(client) -> list[int]:
    """Populate /profile/skills and return list of skill IDs."""
    client.patch("/profile/skills", json={"skills": [
        {"kind": "technical", "name": "Python", "sort_order": 0},
        {"kind": "technical", "name": "FastAPI", "sort_order": 1},
        {"kind": "competency", "name": "Leadership", "sort_order": 0},
    ]})
    skills_resp = client.get("/profile/skills")
    return [s["id"] for s in skills_resp.json()]


def test_import_success(authenticated_client):
    """Import selected master skills into the job profile."""
    client, _, _, job_profile_id = authenticated_client
    skill_ids = _setup_master_skills(client)

    resp = client.post(
        f"{_skills_url(job_profile_id)}/import",
        json={"source_ids": skill_ids[:2]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["imported"]) == 2
    assert data["skipped"] == []
    assert data["not_found"] == []

    # Verify skills appear in job profile
    list_resp = client.get(_skills_url(job_profile_id))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2


def test_import_skips_existing_by_kind_and_name(authenticated_client):
    """Importing the same skills twice skips them the second time."""
    client, _, _, job_profile_id = authenticated_client
    skill_ids = _setup_master_skills(client)

    # First import
    client.post(
        f"{_skills_url(job_profile_id)}/import",
        json={"source_ids": skill_ids},
    )

    # Second import — all should be skipped
    resp = client.post(
        f"{_skills_url(job_profile_id)}/import",
        json={"source_ids": skill_ids},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == []
    assert len(data["skipped"]) == len(skill_ids)
    assert data["not_found"] == []


def test_import_adds_to_existing(authenticated_client):
    """Import appends to skills already set via PATCH."""
    client, _, _, job_profile_id = authenticated_client
    skill_ids = _setup_master_skills(client)

    # PATCH a different skill directly
    _patch_skills(client, job_profile_id, [
        {"kind": "technical", "name": "Docker", "sort_order": 0},
    ])

    # Import "Python" (kind=technical, name=Python) which is not "Docker"
    python_id = next(
        sid for sid in skill_ids
        if client.get(f"/profile/skills/{sid}").json()["name"] == "Python"
    )

    resp = client.post(
        f"{_skills_url(job_profile_id)}/import",
        json={"source_ids": [python_id]},
    )
    assert resp.status_code == 200
    assert len(resp.json()["imported"]) == 1

    # Both Docker and Python should now exist
    list_resp = client.get(_skills_url(job_profile_id))
    names = {s["name"] for s in list_resp.json()}
    assert "Docker" in names
    assert "Python" in names


def test_import_cross_user_not_found(authenticated_client, app):
    """Importing another user's skill IDs returns them as not_found."""
    client, user_data, _, job_profile_id = authenticated_client
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password

    async def _make_other_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(
                conn,
                email=f"jp-skills-other-{uuid.uuid4().hex}@example.com",
                password_hash=hash_password("x"),
            )
            return dict(u)
        finally:
            await conn.close()

    other_user = asyncio.run(_make_other_user())

    async def override_other():
        return other_user

    # Create master skills for the other user using a separate client context
    app.dependency_overrides[get_current_user] = override_other
    with TestClient(app) as other_client:
        other_client.post("/profile")
        other_client.patch("/profile/skills", json={"skills": [
            {"kind": "technical", "name": "Rust", "sort_order": 0},
        ]})
        other_skills = other_client.get("/profile/skills").json()
        other_skill_ids = [s["id"] for s in other_skills]

    # Restore original user override and attempt import
    async def override_original():
        return user_data

    app.dependency_overrides[get_current_user] = override_original
    resp = client.post(
        f"{_skills_url(job_profile_id)}/import",
        json={"source_ids": other_skill_ids},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == []
    assert data["not_found"] == other_skill_ids


def test_import_empty_ids_422(authenticated_client):
    """Importing with an empty source_ids list returns 422."""
    client, _, _, job_profile_id = authenticated_client
    resp = client.post(
        f"{_skills_url(job_profile_id)}/import",
        json={"source_ids": []},
    )
    assert resp.status_code == 422
