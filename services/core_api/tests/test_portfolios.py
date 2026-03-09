"""
Tests for portfolio endpoints with permission enforcement (SP-02).
"""

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database import init_db
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
    resp = client.get("/roles", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    role = next((r for r in resp.json() if r["name"] == role_name), None)
    assert role is not None
    role_id = role["id"]
    resp2 = client.post(f"/users/{user_id}/roles/{role_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 200


class TestPortfolioPermissions:
    def test_po_can_crud_portfolio(self):
        # create process owner account
        po_id, po_token = create_user_and_login("pouser", "po@example.com", "popass")
        assign_role(po_id, "Process Owner", po_token)

        headers = {"Authorization": f"Bearer {po_token}"}
        # create
        resp = client.post("/portfolios", json={"name": "Main", "description": "Main portfolio"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        portfolio_id = data["id"]
        assert data["name"] == "Main"

        # list
        resp2 = client.get("/portfolios", headers=headers)
        assert resp2.status_code == 200
        assert any(p["id"] == portfolio_id for p in resp2.json())

        # get
        resp3 = client.get(f"/portfolios/{portfolio_id}", headers=headers)
        assert resp3.status_code == 200
        assert resp3.json()["name"] == "Main"

        # update
        resp4 = client.put(f"/portfolios/{portfolio_id}", json={"name": "Main Updated", "description": "", "landAreaSqm": 123}, headers=headers)
        assert resp4.status_code == 200
        assert resp4.json()["name"] == "Main Updated"

        # delete
        resp5 = client.delete(f"/portfolios/{portfolio_id}", headers=headers)
        assert resp5.status_code == 200

    def test_self_service_read_only(self):
        # create users
        po_id, po_token = create_user_and_login("po2", "po2@example.com", "po2pass")
        assign_role(po_id, "Process Owner", po_token)
        u_id, u_token = create_user_and_login("ssuser", "ss@example.com", "sspass")
        assign_role(u_id, "Self-Service", po_token)

        po_headers = {"Authorization": f"Bearer {po_token}"}
        ss_headers = {"Authorization": f"Bearer {u_token}"}

        # create portfolio as PO
        resp = client.post("/portfolios", json={"name": "SSTest", "description": ""}, headers=po_headers)
        assert resp.status_code == 200
        portfolio_id = resp.json()["id"]

        # self-service can list and get
        resp2 = client.get("/portfolios", headers=ss_headers)
        assert resp2.status_code == 200
        resp3 = client.get(f"/portfolios/{portfolio_id}", headers=ss_headers)
        assert resp3.status_code == 200

        # cannot create
        resp4 = client.post("/portfolios", json={"name": "X"}, headers=ss_headers)
        assert resp4.status_code == 403

        # cannot update
        resp5 = client.put(f"/portfolios/{portfolio_id}", json={"name": "fail"}, headers=ss_headers)
        assert resp5.status_code == 403

        # cannot delete
        resp6 = client.delete(f"/portfolios/{portfolio_id}", headers=ss_headers)
        assert resp6.status_code == 403
