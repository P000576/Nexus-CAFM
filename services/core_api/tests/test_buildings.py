from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_building():
    response = client.post("/buildings", json={"name": "Test Building"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Building"
    bid = data["id"]

    resp2 = client.get(f"/buildings/{bid}")
    assert resp2.status_code == 200
    assert resp2.json()["id"] == bid
