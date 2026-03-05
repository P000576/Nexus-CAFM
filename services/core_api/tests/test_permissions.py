from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database import init_db, SessionLocal
from seed_rbac import seed_permissions, seed_roles

client = TestClient(app)


def setup_module(module):
    # initialize database and seed RBAC before tests
    init_db()
    seed_permissions()
    seed_roles()


def create_user_and_login(username, email, password):
    resp = client.post("/users", json={
        "username": username,
        "email": email,
        "password": password,
        "firstName": "Test",
        "lastName": "User"
    })
    assert resp.status_code == 200
    user_id = resp.json()["id"]
    login = client.post("/login", data={"username": username, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return user_id, token


def assign_role(user_id, role_name, token):
    # find role id by name
    resp = client.get("/roles", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    role = next((r for r in resp.json() if r["name"] == role_name), None)
    assert role is not None
    role_id = role["id"]
    resp2 = client.post(f"/users/{user_id}/roles/{role_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 200


def test_permission_enforcement():
    # create process owner user to perform initial assignments
    po_id, po_token = create_user_and_login("admin", "admin@example.com", "adminpass")
    # assign Process Owner role to admin
    assign_role(po_id, "Process Owner", po_token)

    # create normal user
    u_id, u_token = create_user_and_login("normal", "normal@example.com", "normalpass")
    # assign Self-Service role
    assign_role(u_id, "Self-Service", po_token)

    # normal user tries to create building -> should be forbidden
    resp = client.post("/buildings", json={"name": "Forbidden"}, headers={"Authorization": f"Bearer {u_token}"})
    assert resp.status_code == 403

    # process owner can create
    resp2 = client.post("/buildings", json={"name": "Allowed"}, headers={"Authorization": f"Bearer {po_token}"})
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "Allowed"
