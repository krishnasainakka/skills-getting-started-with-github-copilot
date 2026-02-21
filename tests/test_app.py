import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Store the original activities data
    original_activities = activities.copy()
    yield
    # Reset activities to original state after each test
    activities.clear()
    activities.update(original_activities)

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)

def test_signup_success(client):
    initial_participants = activities["Chess Club"]["participants"].copy()
    response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert "Signed up newstudent@mergington.edu for Chess Club" == response.json()["message"]
    
    # Verify the participant was added
    response = client.get("/activities")
    assert "newstudent@mergington.edu" in response.json()["Chess Club"]["participants"]
    assert len(response.json()["Chess Club"]["participants"]) == len(initial_participants) + 1

def test_signup_already_signed_up(client):
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    # Attempt duplicate signup
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert "Student already signed up for this activity" == response.json()["detail"]

def test_signup_activity_not_found(client):
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" == response.json()["detail"]

def test_delete_signup_success(client):
    # First signup
    client.post("/activities/Programming%20Class/signup?email=removeme@mergington.edu")
    initial_participants = activities["Programming Class"]["participants"].copy()
    
    # Now delete
    response = client.delete("/activities/Programming%20Class/signup?email=removeme@mergington.edu")
    assert response.status_code == 200
    assert "Unregistered removeme@mergington.edu from Programming Class" == response.json()["message"]
    
    # Verify removed
    response = client.get("/activities")
    assert "removeme@mergington.edu" not in response.json()["Programming Class"]["participants"]
    assert len(response.json()["Programming Class"]["participants"]) == len(initial_participants) - 1

def test_delete_signup_not_signed_up(client):
    response = client.delete("/activities/Chess%20Club/signup?email=notsigned@mergington.edu")
    assert response.status_code == 404
    assert "Participant not found" == response.json()["detail"]

def test_delete_signup_activity_not_found(client):
    response = client.delete("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" == response.json()["detail"]