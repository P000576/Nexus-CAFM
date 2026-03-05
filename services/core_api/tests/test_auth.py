from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_user_login_and_me():
    # create a user first
    resp = client.post("/users", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123",
        "firstName": "Alice",
        "lastName": "Smith"
    }, headers={})
    assert resp.status_code == 200
    user_data = resp.json()
    user_id = user_data["id"]

    # login
    resp2 = client.post("/login", data={"username": "alice", "password": "password123"})
    assert resp2.status_code == 200
    token = resp2.json()["access_token"]
    assert token

    # call /me
    resp3 = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp3.status_code == 200
    assert resp3.json()["username"] == "alice"
