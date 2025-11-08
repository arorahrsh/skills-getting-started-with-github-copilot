from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity: pre-seeded activity exists
    assert "Chess Club" in data


def test_signup_duplicate_and_remove():
    activity_name = "Chess Club"
    enc_name = quote(activity_name, safe="")
    email = "pytest_temp_user@example.com"

    # Backup original participants list and ensure clean state
    original = activities[activity_name]["participants"].copy()
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # Sign up new participant
    resp = client.post(f"/activities/{enc_name}/signup", params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity_name]["participants"]

    # Duplicate signup should return 400
    resp_dup = client.post(f"/activities/{enc_name}/signup", params={"email": email})
    assert resp_dup.status_code == 400

    # Remove the participant
    resp_del = client.delete(f"/activities/{enc_name}/participants", params={"email": email})
    assert resp_del.status_code == 200
    assert email not in activities[activity_name]["participants"]

    # Restore original participants to leave global state unchanged
    activities[activity_name]["participants"] = original
