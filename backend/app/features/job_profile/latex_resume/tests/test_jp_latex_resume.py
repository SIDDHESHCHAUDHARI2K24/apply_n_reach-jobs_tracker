"""Integration tests for job_profile latex_resume endpoints."""
import shutil
import pytest

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
        # job_profile_id is still the same — UNIQUE constraint guarantees one row
        assert resp1.json()["job_profile_id"] == resp2.json()["job_profile_id"]
        # Second render changes the layout
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
