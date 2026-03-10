import copy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module

# keep a pristine copy of the initial in2memory data
initial_activities = copy.deepcopy(app_module.activities)


@pytest.fixture
def client():
    # reset state before every test so they can run in any order
    app_module.activities = copy.deepcopy(initial_activities)
    with TestClient(app_module.app) as c:
        yield c


def test_get_activities(client):
    # Arrange
    expected = initial_activities
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    assert resp.json() == expected


def test_signup_adds_participant_and_duplicate_error(client):
    # Arrange
    activity = "Tennis Club"
    email = "tester@example.com"
    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"

    # Act duplicate signup
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Student already signed up"


def test_unregister_participant_and_errors(client):
    # Arrange
    activity = "Tennis Club"
    existing = "alex@mergington.edu"
    # Act
    resp = client.delete(f"/activities/{activity}/signup", params={"email": existing})
    # Assert
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Unregistered {existing} from {activity}"

    # Act unregistered again
    resp2 = client.delete(f"/activities/{activity}/signup", params={"email": existing})
    # Assert
    assert resp2.status_code == 404
    assert resp2.json()["detail"] == "Student not registered"


def test_unregister_nonexistent_activity(client):
    # Arrange
    bad = "/activities/NoSuch/signup"
    # Act
    resp = client.delete(bad, params={"email": "x@y.com"})
    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"
