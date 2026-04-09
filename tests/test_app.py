import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def restore_activities():
    original_data = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_data))


def test_get_activities_returns_current_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert "description" in data[expected_activity]


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Basketball Team"
    email = "test.student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_duplicate_email_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]
    signup_url = f"/activities/{activity_name}/signup?email={existing_email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success():
    # Arrange
    activity_name = "Programming Class"
    email = activities[activity_name]["participants"][0]
    unregister_url = f"/activities/{activity_name}/unregister?email={email}"

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_400():
    # Arrange
    activity_name = "Gym Class"
    email = "missing.student@mergington.edu"
    unregister_url = f"/activities/{activity_name}/unregister?email={email}"

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
