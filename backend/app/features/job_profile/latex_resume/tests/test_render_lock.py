"""Tests for duplicate render request guardrails."""

from app.features.job_profile.latex_resume import service


class TestRenderLock:
    def test_render_returns_409_when_lock_not_acquired(self, authenticated_client, monkeypatch):
        client, _, jp_id = authenticated_client

        async def fake_acquire_lock(*_args, **_kwargs):
            return False

        monkeypatch.setattr(service, "_acquire_render_lock", fake_acquire_lock)

        response = client.post(f"/job-profiles/{jp_id}/latex-resume/render")

        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"].lower()
