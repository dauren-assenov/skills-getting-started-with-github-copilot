import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# snapshot of initial data so we can reset between tests
_initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def restore_activities():
    """Revert the in-memory activities dictionary to its original state.

    Runs automatically before each test (AAA: Arrange).
    """
    activities.clear()
    activities.update(copy.deepcopy(_initial_activities))
    yield
    # no teardown necessary

client = TestClient(app)


def test_get_activities_returns_initial_data():
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    assert resp.json() == _initial_activities


def test_signup_for_activity_success():
    # Arrange
    target = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    resp = client.post(f"/activities/{target}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in activities[target]["participants"]
    assert resp.json()["message"] == f"Signed up {email} for {target}"


def test_signup_for_activity_twice():
    # Arrange
    target = "Chess Club"
    email = "michael@mergington.edu"  # already enrolled in initial data

    # Act
    first = client.post(f"/activities/{target}/signup", params={"email": email})
    second = client.post(f"/activities/{target}/signup", params={"email": email})

    # Assert
    assert first.status_code == 400 or first.status_code == 200
    assert second.status_code == 400
    assert "already signed up" in second.json()["detail"]


def test_signup_for_nonexistent_activity():
    # Arrange
    target = "Nonexistent"
    email = "foo@bar.com"

    # Act
    resp = client.post(f"/activities/{target}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 404


def test_remove_participant_success():
    # Arrange
    target = "Chess Club"
    email = "daniel@mergington.edu"

    # Act
    resp = client.delete(f"/activities/{target}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in activities[target]["participants"]
    assert "Removed" in resp.json()["message"]


def test_remove_participant_not_found():
    # Arrange
    target = "Chess Club"
    email = "notthere@mergington.edu"

    # Act
    resp = client.delete(f"/activities/{target}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 404


def test_remove_participant_nonexistent_activity():
    # Arrange
    target = "Other"
    email = "someone@mergington.edu"

    # Act
    resp = client.delete(f"/activities/{target}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 404
