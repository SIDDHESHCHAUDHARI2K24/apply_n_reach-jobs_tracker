"""Cross-user isolation tests for all job profile endpoints.

Verifies that User B cannot access, modify, or import from User A's job profiles.
These tests are the final security net against IDOR vulnerabilities.
"""
import uuid
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.utils import get_current_user
from app.features.core.config import settings
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import hash_password


# ---------------------------------------------------------------------------
# Test infrastructure
# ---------------------------------------------------------------------------

async def _make_user(suffix: str = "") -> dict:
    """Create a real user in the DB and return its data dict."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"xuser-{suffix}-{uuid.uuid4().hex}@example.com"
        user = await create_user(conn, email=email, password_hash=hash_password("pass"))
        return dict(user)
    finally:
        await conn.close()


@pytest.fixture
def dual_user_setup():
    """
    Yields (app, client_a, user_a, client_b, user_b).
    User A has a job profile with data populated across all sections.
    User B has their own profile+job_profile (needed for import cross-user tests).
    """
    app = create_app()

    user_a = asyncio.run(_make_user("a"))
    user_b = asyncio.run(_make_user("b"))

    async def override_a(): return user_a
    async def override_b(): return user_b

    # Setup User A
    app.dependency_overrides[get_current_user] = override_a
    with TestClient(app) as client_a:
        client_a.post("/profile")
        jp_resp = client_a.post("/job-profiles", json={
            "profile_name": f"A Profile {uuid.uuid4().hex[:6]}",
            "target_role": "Engineer",
        })
        jp_a_id = jp_resp.json()["id"]

        # Populate all sections for User A
        client_a.patch(f"/job-profiles/{jp_a_id}/personal", json={
            "full_name": "User A",
            "email": "usera@example.com",
            "linkedin_url": "https://linkedin.com/in/usera",
        })
        edu_resp = client_a.post(f"/job-profiles/{jp_a_id}/education", json={
            "university_name": "MIT", "major": "CS", "degree_type": "BS",
            "start_month_year": "09/2018", "end_month_year": "06/2022",
        })
        edu_id = edu_resp.json()["id"]

        exp_resp = client_a.post(f"/job-profiles/{jp_a_id}/experience", json={
            "role_title": "Engineer", "company_name": "Google",
            "start_month_year": "07/2022", "context": "Work",
        })
        exp_id = exp_resp.json()["id"]

        proj_resp = client_a.post(f"/job-profiles/{jp_a_id}/projects", json={
            "project_name": "My App", "description": "Cool app",
        })
        proj_id = proj_resp.json()["id"]

        res_resp = client_a.post(f"/job-profiles/{jp_a_id}/research", json={
            "paper_name": "AI Paper",
            "publication_link": "https://arxiv.org/abs/1234",
            "description": "Research",
        })
        res_id = res_resp.json()["id"]

        cert_resp = client_a.post(f"/job-profiles/{jp_a_id}/certifications", json={
            "certification_name": "AWS SAA",
            "verification_link": "https://aws.amazon.com/cert",
        })
        cert_id = cert_resp.json()["id"]

        client_a.patch(f"/job-profiles/{jp_a_id}/skills", json={"skills": [
            {"kind": "technical", "name": "Python", "sort_order": 0},
        ]})
        skills_resp = client_a.get(f"/job-profiles/{jp_a_id}/skills")
        skill_id = skills_resp.json()[0]["id"]

        section_ids = {
            "jp_a_id": jp_a_id,
            "edu_id": edu_id,
            "exp_id": exp_id,
            "proj_id": proj_id,
            "res_id": res_id,
            "cert_id": cert_id,
            "skill_id": skill_id,
        }

    # Setup User B (needs own profile for import tests)
    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as client_b:
        client_b.post("/profile")
        jp_b_resp = client_b.post("/job-profiles", json={
            "profile_name": f"B Profile {uuid.uuid4().hex[:6]}"
        })
        jp_b_id = jp_b_resp.json()["id"]
        section_ids["jp_b_id"] = jp_b_id

    app.dependency_overrides.clear()

    yield app, override_a, override_b, user_a, user_b, section_ids
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Core job profile isolation
# ---------------------------------------------------------------------------

class TestJobProfileCoreIsolation:
    def test_user_b_cannot_get_user_a_job_profile(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.get(f"/job-profiles/{ids['jp_a_id']}")
            assert resp.status_code == 404

    def test_user_b_cannot_patch_user_a_job_profile(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.patch(f"/job-profiles/{ids['jp_a_id']}", json={
                "profile_name": "hacked"
            })
            assert resp.status_code == 404

    def test_user_b_cannot_delete_user_a_job_profile(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.delete(f"/job-profiles/{ids['jp_a_id']}")
            assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Personal section isolation
# ---------------------------------------------------------------------------

class TestPersonalSectionIsolation:
    def test_get_personal_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.get(f"/job-profiles/{ids['jp_a_id']}/personal")
            assert resp.status_code == 404

    def test_patch_personal_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.patch(f"/job-profiles/{ids['jp_a_id']}/personal", json={
                "full_name": "Hacker", "email": "h@h.com",
                "linkedin_url": "https://linkedin.com/in/hacker",
            })
            assert resp.status_code == 404

    def test_import_personal_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(f"/job-profiles/{ids['jp_a_id']}/personal/import")
            assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Education section isolation
# ---------------------------------------------------------------------------

class TestEducationSectionIsolation:
    def test_list_education_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.get(f"/job-profiles/{ids['jp_a_id']}/education")
            assert resp.status_code == 404

    def test_add_education_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(f"/job-profiles/{ids['jp_a_id']}/education", json={
                "university_name": "Hack U", "major": "CS", "degree_type": "BS",
                "start_month_year": "09/2020",
            })
            assert resp.status_code == 404

    def test_patch_education_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.patch(
                f"/job-profiles/{ids['jp_a_id']}/education/{ids['edu_id']}",
                json={"major": "hacked"},
            )
            assert resp.status_code == 404

    def test_delete_education_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.delete(
                f"/job-profiles/{ids['jp_a_id']}/education/{ids['edu_id']}"
            )
            assert resp.status_code == 404

    def test_import_education_cross_user_not_found(self, dual_user_setup):
        """User B cannot import User A's education into User B's own job profile."""
        app, override_a, override_b, _, _, ids = dual_user_setup
        # First create a master education entry as User A
        app.dependency_overrides[get_current_user] = override_a
        with TestClient(app) as client_a:
            master_edu = client_a.post("/profile/education", json={
                "university_name": "MIT", "major": "CS", "degree_type": "BS",
                "start_month_year": "09/2018",
            }).json()

        # User B tries to import User A's master education into User B's job profile
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(
                f"/job-profiles/{ids['jp_b_id']}/education/import",
                json={"source_ids": [master_edu["id"]]},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert master_edu["id"] in data["not_found"]
            assert data["imported"] == []


# ---------------------------------------------------------------------------
# Experience section isolation
# ---------------------------------------------------------------------------

class TestExperienceSectionIsolation:
    def test_list_experience_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            assert client_b.get(f"/job-profiles/{ids['jp_a_id']}/experience").status_code == 404

    def test_add_experience_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(f"/job-profiles/{ids['jp_a_id']}/experience", json={
                "role_title": "Hacker", "company_name": "Evil Corp",
                "start_month_year": "01/2023", "context": "malicious",
            })
            assert resp.status_code == 404

    def test_patch_experience_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.patch(
                f"/job-profiles/{ids['jp_a_id']}/experience/{ids['exp_id']}",
                json={"role_title": "hacked"},
            )
            assert resp.status_code == 404

    def test_delete_experience_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.delete(
                f"/job-profiles/{ids['jp_a_id']}/experience/{ids['exp_id']}"
            )
            assert resp.status_code == 404

    def test_import_experience_cross_user_not_found(self, dual_user_setup):
        app, override_a, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_a
        with TestClient(app) as client_a:
            master_exp = client_a.post("/profile/experience", json={
                "role_title": "Eng", "company_name": "Google",
                "start_month_year": "07/2022", "context": "Work",
            }).json()

        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(
                f"/job-profiles/{ids['jp_b_id']}/experience/import",
                json={"source_ids": [master_exp["id"]]},
            )
            assert resp.status_code == 200
            assert master_exp["id"] in resp.json()["not_found"]


# ---------------------------------------------------------------------------
# Projects section isolation
# ---------------------------------------------------------------------------

class TestProjectsSectionIsolation:
    def test_list_projects_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            assert client_b.get(f"/job-profiles/{ids['jp_a_id']}/projects").status_code == 404

    def test_add_project_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(f"/job-profiles/{ids['jp_a_id']}/projects", json={
                "project_name": "Hack", "description": "Bad"
            })
            assert resp.status_code == 404

    def test_patch_project_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.patch(
                f"/job-profiles/{ids['jp_a_id']}/projects/{ids['proj_id']}",
                json={"project_name": "hacked"},
            )
            assert resp.status_code == 404

    def test_delete_project_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.delete(
                f"/job-profiles/{ids['jp_a_id']}/projects/{ids['proj_id']}"
            )
            assert resp.status_code == 404

    def test_import_projects_cross_user_not_found(self, dual_user_setup):
        app, override_a, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_a
        with TestClient(app) as client_a:
            master_proj = client_a.post("/profile/projects", json={
                "project_name": "A App", "description": "A project",
                "start_month_year": "01/2023",
            }).json()

        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(
                f"/job-profiles/{ids['jp_b_id']}/projects/import",
                json={"source_ids": [master_proj["id"]]},
            )
            assert resp.status_code == 200
            assert master_proj["id"] in resp.json()["not_found"]


# ---------------------------------------------------------------------------
# Research section isolation
# ---------------------------------------------------------------------------

class TestResearchSectionIsolation:
    def test_list_research_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            assert client_b.get(f"/job-profiles/{ids['jp_a_id']}/research").status_code == 404

    def test_add_research_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(f"/job-profiles/{ids['jp_a_id']}/research", json={
                "paper_name": "Hack Paper",
                "publication_link": "https://arxiv.org/abs/9999",
                "description": "Bad",
            })
            assert resp.status_code == 404

    def test_patch_research_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.patch(
                f"/job-profiles/{ids['jp_a_id']}/research/{ids['res_id']}",
                json={"paper_name": "hacked"},
            )
            assert resp.status_code == 404

    def test_delete_research_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.delete(
                f"/job-profiles/{ids['jp_a_id']}/research/{ids['res_id']}"
            )
            assert resp.status_code == 404

    def test_import_research_cross_user_not_found(self, dual_user_setup):
        app, override_a, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_a
        with TestClient(app) as client_a:
            master_res = client_a.post("/profile/research", json={
                "paper_name": "A Paper",
                "publication_link": "https://arxiv.org/abs/111",
                "description": "Research",
            }).json()

        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(
                f"/job-profiles/{ids['jp_b_id']}/research/import",
                json={"source_ids": [master_res["id"]]},
            )
            assert resp.status_code == 200
            assert master_res["id"] in resp.json()["not_found"]


# ---------------------------------------------------------------------------
# Certifications section isolation
# ---------------------------------------------------------------------------

class TestCertificationsSectionIsolation:
    def test_list_certifications_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            assert client_b.get(f"/job-profiles/{ids['jp_a_id']}/certifications").status_code == 404

    def test_add_certification_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(f"/job-profiles/{ids['jp_a_id']}/certifications", json={
                "certification_name": "Hack Cert",
                "verification_link": "https://hack.com/cert",
            })
            assert resp.status_code == 404

    def test_patch_certification_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.patch(
                f"/job-profiles/{ids['jp_a_id']}/certifications/{ids['cert_id']}",
                json={"certification_name": "hacked"},
            )
            assert resp.status_code == 404

    def test_delete_certification_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.delete(
                f"/job-profiles/{ids['jp_a_id']}/certifications/{ids['cert_id']}"
            )
            assert resp.status_code == 404

    def test_import_certifications_cross_user_not_found(self, dual_user_setup):
        app, override_a, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_a
        with TestClient(app) as client_a:
            master_cert = client_a.post("/profile/certifications", json={
                "certification_name": "AWS SAA",
                "verification_link": "https://aws.amazon.com/cert",
            }).json()

        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(
                f"/job-profiles/{ids['jp_b_id']}/certifications/import",
                json={"source_ids": [master_cert["id"]]},
            )
            assert resp.status_code == 200
            assert master_cert["id"] in resp.json()["not_found"]


# ---------------------------------------------------------------------------
# Skills section isolation
# ---------------------------------------------------------------------------

class TestSkillsSectionIsolation:
    def test_list_skills_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            assert client_b.get(f"/job-profiles/{ids['jp_a_id']}/skills").status_code == 404

    def test_replace_skills_cross_user_404(self, dual_user_setup):
        app, _, override_b, _, _, ids = dual_user_setup
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.patch(
                f"/job-profiles/{ids['jp_a_id']}/skills",
                json={"skills": [{"kind": "technical", "name": "Python", "sort_order": 0}]},
            )
            assert resp.status_code == 404

    def test_import_skills_cross_user_not_found(self, dual_user_setup):
        app, override_a, override_b, _, _, ids = dual_user_setup
        # Get User A's master skill IDs
        app.dependency_overrides[get_current_user] = override_a
        with TestClient(app) as client_a:
            client_a.patch("/profile/skills", json={"skills": [
                {"kind": "technical", "name": "Python", "sort_order": 0},
            ]})
            skills = client_a.get("/profile/skills").json()
            skill_ids = [s["id"] for s in skills]

        # User B tries to import User A's skills
        app.dependency_overrides[get_current_user] = override_b
        with TestClient(app) as client_b:
            resp = client_b.post(
                f"/job-profiles/{ids['jp_b_id']}/skills/import",
                json={"source_ids": skill_ids},
            )
            assert resp.status_code == 200
            assert all(sid in resp.json()["not_found"] for sid in skill_ids)
