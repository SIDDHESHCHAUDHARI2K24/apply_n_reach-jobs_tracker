"""Integration tests for job profile certifications endpoints."""
import uuid
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.features.job_profile.tests.conftest import _create_job_profile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cert_payload(**overrides):
    base = {
        "certification_name": "AWS SAA",
        "verification_link": "https://aws.amazon.com/cert",
    }
    base.update(overrides)
    return base


def _create_cert(client, jp_id, **overrides):
    resp = client.post(f"/job-profiles/{jp_id}/certifications", json=_cert_payload(**overrides))
    assert resp.status_code == 201, f"Failed to create certification: {resp.status_code} {resp.text}"
    return resp.json()


def _create_master_cert(client):
    resp = client.post("/profile/certifications", json={
        "certification_name": "AWS SAA",
        "verification_link": "https://aws.amazon.com/cert",
    })
    assert resp.status_code == 201, f"Failed to create master certification: {resp.status_code} {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_list_empty(authenticated_client):
    """1. Listing certifications on a new job profile returns an empty list."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    resp = client.get(f"/job-profiles/{jp['id']}/certifications")
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_and_list(authenticated_client):
    """2. Adding a certification entry and then listing returns it."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    _create_cert(client, jp["id"])
    resp = client.get(f"/job-profiles/{jp['id']}/certifications")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["certification_name"] == "AWS SAA"
    assert data[0]["verification_link"] == "https://aws.amazon.com/cert"
    assert data[0]["job_profile_id"] == jp["id"]


def test_get_by_id(authenticated_client):
    """3. Fetching a certification entry by ID returns the correct item."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_cert(client, jp["id"])
    resp = client.get(f"/job-profiles/{jp['id']}/certifications/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]
    assert resp.json()["certification_name"] == "AWS SAA"


def test_update_single_field(authenticated_client):
    """4. PATCH with only certification_name updates just that field."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_cert(client, jp["id"])
    resp = client.patch(
        f"/job-profiles/{jp['id']}/certifications/{created['id']}",
        json={"certification_name": "Google Cloud Pro"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["certification_name"] == "Google Cloud Pro"
    # Other fields unchanged
    assert data["verification_link"] == created["verification_link"]


def test_delete(authenticated_client):
    """5. Deleting a certification entry returns 204 and it's gone."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_cert(client, jp["id"])
    resp = client.delete(f"/job-profiles/{jp['id']}/certifications/{created['id']}")
    assert resp.status_code == 204
    resp2 = client.get(f"/job-profiles/{jp['id']}/certifications/{created['id']}")
    assert resp2.status_code == 404


def test_partial_update_empty_body_400(authenticated_client):
    """6. PATCH with an empty body returns 400."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_cert(client, jp["id"])
    resp = client.patch(
        f"/job-profiles/{jp['id']}/certifications/{created['id']}",
        json={},
    )
    assert resp.status_code == 400


def test_html_stripped(authenticated_client):
    """7. HTML tags in certification_name are stripped by sanitize_text."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    resp = client.post(
        f"/job-profiles/{jp['id']}/certifications",
        json=_cert_payload(certification_name="<b>AWS</b> SAA"),
    )
    assert resp.status_code == 201
    assert resp.json()["certification_name"] == "AWS SAA"


def test_cross_user_returns_404(app):
    """8. Accessing another user's job profile certifications returns 404."""
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(
                conn,
                email=f"jp-cert-cross-{uuid.uuid4().hex}@example.com",
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
        entry = ca.post(f"/job-profiles/{jp['id']}/certifications", json=_cert_payload()).json()

    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as cb:
        resp = cb.get(f"/job-profiles/{jp['id']}/certifications/{entry['id']}")
        assert resp.status_code == 404

    app.dependency_overrides.clear()


def test_unauthenticated_401(client):
    """9. Unauthenticated requests to certifications endpoint return 401."""
    resp = client.get("/job-profiles/1/certifications")
    assert resp.status_code == 401


def test_source_certification_id_null(authenticated_client):
    """10. Manually added certification entries have source_certification_id=null."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    created = _create_cert(client, jp["id"])
    assert created["source_certification_id"] is None


def test_import_success(authenticated_client):
    """11. Importing a master certification entry succeeds."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    master = _create_master_cert(client)
    resp = client.post(
        f"/job-profiles/{jp['id']}/certifications/import",
        json={"source_ids": [master["id"]]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert master["id"] in data["imported"]
    assert data["skipped"] == []
    assert data["not_found"] == []

    # Verify the entry was created with correct source_certification_id
    list_resp = client.get(f"/job-profiles/{jp['id']}/certifications")
    assert list_resp.status_code == 200
    entries = list_resp.json()
    assert len(entries) == 1
    assert entries[0]["source_certification_id"] == master["id"]
    assert entries[0]["certification_name"] == master["certification_name"]


def test_import_skips_duplicates(authenticated_client):
    """12. Importing the same certification entry twice skips the second import."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    master = _create_master_cert(client)

    # First import
    client.post(
        f"/job-profiles/{jp['id']}/certifications/import",
        json={"source_ids": [master["id"]]},
    )

    # Second import — should skip
    resp = client.post(
        f"/job-profiles/{jp['id']}/certifications/import",
        json={"source_ids": [master["id"]]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == []
    assert master["id"] in data["skipped"]

    # Only one entry total
    list_resp = client.get(f"/job-profiles/{jp['id']}/certifications")
    assert len(list_resp.json()) == 1


def test_import_cross_user_not_found(app):
    """13. Importing another user's certification returns not_found."""
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password

    async def _make_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            u = await create_user(
                conn,
                email=f"jp-cert-import-cross-{uuid.uuid4().hex}@example.com",
                password_hash=hash_password("x"),
            )
            return dict(u)
        finally:
            await conn.close()

    user_a = asyncio.run(_make_user())
    user_b = asyncio.run(_make_user())

    # User A creates a master certification entry
    async def override_a():
        return user_a

    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as ca:
        ca.post("/profile")
        master = ca.post("/profile/certifications", json={
            "certification_name": "Private Cert",
            "verification_link": "https://example.com/verify",
        }).json()

    # User B tries to import User A's certification into their own job profile
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
            f"/job-profiles/{jp['id']}/certifications/import",
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
        f"/job-profiles/{jp['id']}/certifications/import",
        json={"source_ids": []},
    )
    assert resp.status_code == 422


def test_delete_master_nullifies_source_id(authenticated_client):
    """15. Deleting the master certification entry sets source_certification_id to NULL."""
    client, user_data, _ = authenticated_client
    jp = _create_job_profile(client)
    master = _create_master_cert(client)

    # Import master certification into job profile
    client.post(
        f"/job-profiles/{jp['id']}/certifications/import",
        json={"source_ids": [master["id"]]},
    )

    # Delete master certification
    del_resp = client.delete(f"/profile/certifications/{master['id']}")
    assert del_resp.status_code == 204

    # Verify source_certification_id is now NULL
    list_resp = client.get(f"/job-profiles/{jp['id']}/certifications")
    entries = list_resp.json()
    assert len(entries) == 1
    assert entries[0]["source_certification_id"] is None
    assert entries[0]["certification_name"] == master["certification_name"]
