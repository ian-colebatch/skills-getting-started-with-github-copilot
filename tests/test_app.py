from fastapi.testclient import TestClient
from src.app import app
import uuid

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic smoke checks
    assert isinstance(data, dict)
    assert "Soccer Team" in data


def test_signup_and_remove_participant():
    activity = "Chess Club"
    # generate unique email so tests are idempotent
    email = f"test+{uuid.uuid4().hex}@example.com"

    # sign up
    signup_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # verify participant appears in activity
    activities_resp = client.get("/activities")
    assert activities_resp.status_code == 200
    activities = activities_resp.json()
    assert email in activities[activity]["participants"]

    # remove participant
    del_resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert del_resp.status_code == 200
    assert "Unregistered" in del_resp.json().get("message", "")

    # ensure removed
    activities_resp2 = client.get("/activities")
    activities2 = activities_resp2.json()
    assert email not in activities2[activity]["participants"]

    # deleting again should produce 404
    del_resp2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert del_resp2.status_code == 404
