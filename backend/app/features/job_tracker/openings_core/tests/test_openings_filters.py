"""Tests for job opening list filtering and cursor pagination."""
import uuid


def _create_opening(client, company_name, role_name, initial_status="Interested"):
    resp = client.post(
        "/job-openings",
        json={
            "company_name": company_name,
            "role_name": role_name,
            "initial_status": initial_status,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def test_list_status_filter(auth_client):
    client, _ = auth_client
    tag = uuid.uuid4().hex[:8]
    _create_opening(client, f"Alpha {tag}", "Dev", "Interested")
    _create_opening(client, f"Beta {tag}", "Dev", "Applied")
    _create_opening(client, f"Gamma {tag}", "Dev", "Applied")

    resp = client.get("/job-openings?status=Applied")
    assert resp.status_code == 200
    body = resp.json()
    for item in body["items"]:
        assert item["current_status"] == "Applied"

    # Verify our two Applied ones are present
    names = {item["company_name"] for item in body["items"]}
    assert f"Beta {tag}" in names
    assert f"Gamma {tag}" in names


def test_list_company_name_ilike(auth_client):
    client, _ = auth_client
    tag = uuid.uuid4().hex[:8]
    _create_opening(client, f"Searchable Inc {tag}", "Engineer")
    _create_opening(client, f"Other Corp {tag}", "Engineer")

    resp = client.get(f"/job-openings?company_name=searchable+inc+{tag}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) >= 1
    for item in body["items"]:
        assert tag in item["company_name"].lower() or "searchable" in item["company_name"].lower()


def test_list_role_name_ilike(auth_client):
    client, _ = auth_client
    tag = uuid.uuid4().hex[:8]
    _create_opening(client, f"Corp {tag}", f"UniqueRole {tag}")
    _create_opening(client, f"Corp2 {tag}", "Something Else")

    resp = client.get(f"/job-openings?role_name=uniquerole+{tag}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) >= 1
    for item in body["items"]:
        assert tag in item["role_name"]


def test_list_cursor_pagination(auth_client):
    client, _ = auth_client
    tag = uuid.uuid4().hex[:8]
    # Create 5 openings with unique role_name tag
    created = []
    for i in range(5):
        o = _create_opening(client, f"PagCo {tag}", f"Role {tag} {i}")
        created.append(o)

    role_filter = f"Role {tag}"

    # Get first 3
    resp = client.get(f"/job-openings?role_name={role_filter}&limit=3")
    assert resp.status_code == 200
    page1 = resp.json()
    assert len(page1["items"]) == 3
    assert page1["has_more"] is True
    assert page1["next_cursor"] is not None

    # Get next page using after_id
    cursor = page1["next_cursor"]
    resp2 = client.get(f"/job-openings?role_name={role_filter}&limit=3&after_id={cursor}")
    assert resp2.status_code == 200
    page2 = resp2.json()
    assert len(page2["items"]) >= 2  # 2 remaining (or more if others exist)

    # All ids in page2 should be > cursor
    for item in page2["items"]:
        assert item["id"] > cursor


def test_list_no_has_more_when_exact_limit(auth_client):
    client, _ = auth_client
    tag = uuid.uuid4().hex[:8]
    for i in range(2):
        _create_opening(client, f"ExactCo {tag}", f"ExactRole {tag} {i}")

    resp = client.get(f"/job-openings?role_name=ExactRole+{tag}&limit=2")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["has_more"] is False
    assert body["next_cursor"] is None
