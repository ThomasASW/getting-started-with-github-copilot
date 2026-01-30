"""Tests for FastAPI extracurricular activities application"""

import pytest


class TestActivityEndpoints:
    """Tests for activity retrieval endpoints"""
    
    def test_root_redirect(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
    
    def test_get_activities_success(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_structure(self, client, reset_activities):
        """Test that activity data has correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_has_initial_participants(self, client, reset_activities):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for activity signup functionality"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_signed_up(self, client, reset_activities):
        """Test signup when student is already enrolled"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students signing up for same activity"""
        client.post(
            "/activities/Programming Class/signup",
            params={"email": "student1@mergington.edu"}
        )
        client.post(
            "/activities/Programming Class/signup",
            params={"email": "student2@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Programming Class"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregisterEndpoint:
    """Tests for activity unregistration functionality"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregister when student is not enrolled"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notmember@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_signup_and_unregister_cycle(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "cycletest@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Basketball Club/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        assert email in response.json()["Basketball Club"]["participants"]
        
        # Unregister
        client.post(
            "/activities/Basketball Club/unregister",
            params={"email": email}
        )
        
        response = client.get("/activities")
        assert email not in response.json()["Basketball Club"]["participants"]
