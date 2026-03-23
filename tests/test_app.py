"""
Tests for the Mergington High School Management System API.
Uses FastAPI TestClient for endpoint testing.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture that provides a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture that resets activities to initial state before each test to avoid cross-test pollution."""
    initial_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_data(self, client):
        # Arrange: TestClient is ready
        
        # Act: Make GET request to /activities
        response = client.get("/activities")
        
        # Assert: Response status and content
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "description" in data["Chess Club"]
        assert "schedule" in data["Chess Club"]
        assert "max_participants" in data["Chess Club"]
        assert "participants" in data["Chess Club"]
        assert isinstance(data["Chess Club"]["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client):
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        
        # Act: Sign up for an activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify success response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student(self, client):
        # Arrange: Sign up a student first time
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act: Attempt to sign up the same student again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify error response with meaningful detail
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_activity_not_found_signup(self, client):
        # Arrange: Prepare invalid activity name
        activity_name = "NonexistentActivity"
        email = "test@mergington.edu"
        
        # Act: Attempt to sign up for nonexistent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_success(self, client):
        # Arrange: Add a participant to an activity
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        activities[activity_name]["participants"].append(email)
        
        # Act: Remove the participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert: Verify successful removal
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        assert email not in activities[activity_name]["participants"]

    def test_remove_participant_not_found(self, client):
        # Arrange: Prepare a nonexistent participant
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act: Attempt to remove nonexistent participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_remove_participant_activity_not_found(self, client):
        # Arrange: Prepare invalid activity name
        activity_name = "NonexistentActivity"
        email = "test@mergington.edu"
        
        # Act: Attempt to remove from nonexistent activity
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()