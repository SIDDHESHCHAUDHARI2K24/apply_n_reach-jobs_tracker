"""Tests for agent router endpoints."""
import pytest
from unittest.mock import patch, AsyncMock


class TestAgentRouterEndpoints:
    """Test agent API endpoints."""

    def test_start_agent_run_returns_202(self, auth_client):
        """POST /agent/run should return 202 with run_id."""
        client, user_data, opening_data, profile_data = auth_client

        # Mock the background task to avoid actual agent execution
        with patch(
            "app.features.job_tracker.agents.router._run_agent_background",
            new_callable=AsyncMock,
        ):
            resp = client.post(f"/job-openings/{opening_data['id']}/agent/run")

        assert resp.status_code == 202
        data = resp.json()
        assert "run_id" in data
        assert data["opening_id"] == opening_data["id"]
        assert data["status"] == "running"

    def test_start_agent_run_404_wrong_opening(self, auth_client):
        """POST /agent/run with non-existent opening should 404."""
        client, _, _, _ = auth_client
        resp = client.post("/job-openings/999999/agent/run")
        assert resp.status_code == 404

    def test_get_agent_status(self, auth_client):
        """GET /agent/status should return current agent state."""
        client, user_data, opening_data, profile_data = auth_client
        resp = client.get(f"/job-openings/{opening_data['id']}/agent/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["opening_id"] == opening_data["id"]
        assert data["agent_status"] == "idle"

    def test_list_agent_runs_empty(self, auth_client):
        """GET /agent/runs should return empty list initially."""
        client, _, opening_data, _ = auth_client
        resp = client.get(f"/job-openings/{opening_data['id']}/agent/runs")

        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_agent_runs_after_start(self, auth_client):
        """GET /agent/runs should include runs after starting one."""
        client, _, opening_data, _ = auth_client

        with patch(
            "app.features.job_tracker.agents.router._run_agent_background",
            new_callable=AsyncMock,
        ):
            client.post(f"/job-openings/{opening_data['id']}/agent/run")

        resp = client.get(f"/job-openings/{opening_data['id']}/agent/runs")
        assert resp.status_code == 200
        runs = resp.json()
        assert len(runs) >= 1
        assert runs[0]["status"] == "running"

    def test_duplicate_agent_run_409(self, auth_client):
        """Starting an agent while one is running should return 409."""
        client, _, opening_data, _ = auth_client

        with patch(
            "app.features.job_tracker.agents.router._run_agent_background",
            new_callable=AsyncMock,
        ):
            resp1 = client.post(f"/job-openings/{opening_data['id']}/agent/run")
            assert resp1.status_code == 202

            resp2 = client.post(f"/job-openings/{opening_data['id']}/agent/run")
            assert resp2.status_code == 409
