"""Tests for job_profile latex_resume — endpoint integration and template builder unit tests."""
import shutil
import pytest

from app.features.job_profile.latex_resume.template_builder import (
    _build_projects,
    _build_research,
)

pdflatex_available = shutil.which("pdflatex") is not None
skip_no_pdflatex = pytest.mark.skipif(
    not pdflatex_available,
    reason="pdflatex not installed"
)


class TestRenderEndpoint:
    @skip_no_pdflatex
    def test_render_defaults(self, authenticated_client):
        client, _, jp_id = authenticated_client
        resp = client.post(f"/job-profiles/{jp_id}/latex-resume/render")
        assert resp.status_code == 200
        body = resp.json()
        assert body["job_profile_id"] == jp_id
        assert body["template_name"] == "jakes_resume_v1"
        assert "rendered_at" in body
        layout = body["layout_json"]
        assert layout["body_font_size_pt"] == 10
        assert layout["name_font_size_pt"] == 14

    @skip_no_pdflatex
    def test_render_custom_layout(self, authenticated_client):
        client, _, jp_id = authenticated_client
        resp = client.post(
            f"/job-profiles/{jp_id}/latex-resume/render",
            json={"layout": {"body_font_size_pt": 11}},
        )
        assert resp.status_code == 200
        assert resp.json()["layout_json"]["body_font_size_pt"] == 11

    @skip_no_pdflatex
    def test_overwrite_single_row(self, authenticated_client):
        """Two renders must produce exactly one row (upsert)."""
        client, _, jp_id = authenticated_client
        resp1 = client.post(f"/job-profiles/{jp_id}/latex-resume/render")
        assert resp1.status_code == 200
        resp2 = client.post(
            f"/job-profiles/{jp_id}/latex-resume/render",
            json={"layout": {"body_font_size_pt": 11}},
        )
        assert resp2.status_code == 200
        assert resp1.json()["job_profile_id"] == resp2.json()["job_profile_id"]
        assert resp2.json()["layout_json"]["body_font_size_pt"] == 11


class TestMetadataEndpoint:
    def test_get_metadata_404_when_not_rendered(self, authenticated_client):
        client, _, jp_id = authenticated_client
        resp = client.get(f"/job-profiles/{jp_id}/latex-resume")
        assert resp.status_code == 404

    @skip_no_pdflatex
    def test_get_metadata_200_after_render(self, authenticated_client):
        client, _, jp_id = authenticated_client
        client.post(f"/job-profiles/{jp_id}/latex-resume/render")
        resp = client.get(f"/job-profiles/{jp_id}/latex-resume")
        assert resp.status_code == 200
        body = resp.json()
        assert body["job_profile_id"] == jp_id
        assert body["template_name"] == "jakes_resume_v1"
        assert "rendered_at" in body
        assert isinstance(body["layout_json"], dict)


class TestPdfEndpoint:
    def test_get_pdf_404_when_not_rendered(self, authenticated_client):
        client, _, jp_id = authenticated_client
        resp = client.get(f"/job-profiles/{jp_id}/latex-resume/pdf")
        assert resp.status_code == 404

    @skip_no_pdflatex
    def test_get_pdf_200_after_render(self, authenticated_client):
        client, _, jp_id = authenticated_client
        client.post(f"/job-profiles/{jp_id}/latex-resume/render")
        resp = client.get(f"/job-profiles/{jp_id}/latex-resume/pdf")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert "content-disposition" in resp.headers
        assert resp.content[:4] == b"%PDF"


class TestAuthEndpoints:
    def test_401_render_without_auth(self, client):
        resp = client.post("/job-profiles/1/latex-resume/render")
        assert resp.status_code == 401

    def test_401_metadata_without_auth(self, client):
        resp = client.get("/job-profiles/1/latex-resume")
        assert resp.status_code == 401

    def test_401_pdf_without_auth(self, client):
        resp = client.get("/job-profiles/1/latex-resume/pdf")
        assert resp.status_code == 401


class TestTemplateBuilderProjects:
    def test_technologies_appear_in_projects_section(self):
        """Projects with technologies render the technologies line in LaTeX."""
        projects = [
            {
                "project_name": "My Project",
                "description": "A cool project.",
                "start_month_year": "01/2023",
                "end_month_year": "06/2023",
                "reference_links": [],
                "technologies": ["Python", "FastAPI"],
            }
        ]
        latex = _build_projects(projects)
        assert "Technologies: Python, FastAPI" in latex

    def test_technologies_special_chars_escaped(self):
        """Technologies containing LaTeX special characters are escaped."""
        projects = [
            {
                "project_name": "My Project",
                "description": "Desc.",
                "reference_links": [],
                "technologies": ["C++", "AT&T SDK"],
            }
        ]
        latex = _build_projects(projects)
        assert r"C++" in latex
        assert r"\&" in latex

    def test_no_technologies_field_omits_line(self):
        """Projects without technologies do not produce a Technologies line."""
        projects = [
            {
                "project_name": "My Project",
                "description": "Desc.",
                "reference_links": [],
            }
        ]
        latex = _build_projects(projects)
        assert "Technologies:" not in latex

    def test_empty_technologies_list_omits_line(self):
        """Projects with an empty technologies list do not produce a Technologies line."""
        projects = [
            {
                "project_name": "My Project",
                "description": "Desc.",
                "reference_links": [],
                "technologies": [],
            }
        ]
        latex = _build_projects(projects)
        assert "Technologies:" not in latex

    def test_blank_technology_entries_are_filtered(self):
        """Blank strings in technologies list are ignored."""
        projects = [
            {
                "project_name": "My Project",
                "description": "Desc.",
                "reference_links": [],
                "technologies": ["Python", "  ", ""],
            }
        ]
        latex = _build_projects(projects)
        assert "Technologies: Python" in latex


class TestTemplateBuilderResearch:
    def test_journal_and_year_appear_in_heading(self):
        """Research with journal and year shows both in the project heading."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
                "journal": "Nature",
                "year": "2024",
            }
        ]
        latex = _build_research(researches)
        assert "Nature" in latex
        assert "2024" in latex
        assert r"\textit" in latex

    def test_journal_only_appears_in_heading(self):
        """Research with only journal (no year) still renders the journal."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
                "journal": "Science",
                "year": None,
            }
        ]
        latex = _build_research(researches)
        assert "Science" in latex
        assert r"\textit" in latex

    def test_year_only_appears_in_heading(self):
        """Research with only year (no journal) still renders the year."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
                "journal": None,
                "year": "2023",
            }
        ]
        latex = _build_research(researches)
        assert "2023" in latex
        assert r"\textit" in latex

    def test_no_journal_year_omits_textit(self):
        """Research without journal or year has no \\textit in the heading."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
            }
        ]
        latex = _build_research(researches)
        assert r"\textit" not in latex

    def test_journal_year_special_chars_escaped(self):
        """Journal name with LaTeX special chars is escaped."""
        researches = [
            {
                "paper_name": "My Paper",
                "publication_link": "",
                "description": "",
                "journal": "IEEE & ACM",
                "year": "2024",
            }
        ]
        latex = _build_research(researches)
        assert r"\&" in latex
