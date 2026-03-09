"""
Tests for desk endpoints with permission enforcement (SP-02/04).
"""

from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db
from seed_rbac import seed_permissions, seed_roles

client = TestClient(app)

def setup_module(module):
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


class TestDeskPermissions:
    def setup_class(self):
        # create PO user for setup
        self.po_id, self.po_token = create_user_and_login("po_desk", "po_desk@example.com", "pass")
        assign_role(self.po_id, "Process Owner", self.po_token)
        self.po_headers = {"Authorization": f"Bearer {self.po_token}"}
        # create minimal hierarchy
        resp = client.post("/portfolios", json={"name": "DeskPortfolio"}, headers=self.po_headers)
        assert resp.status_code == 200
        self.portfolio_id = resp.json()["id"]
        # building
        resp = client.post("/buildings", json={"name": "B1", "portfolioId": self.portfolio_id}, headers=self.po_headers)
        assert resp.status_code == 200
        self.building_id = resp.json()["id"]
        # floor
        resp = client.post("/floors", json={"name": "F1", "buildingId": self.building_id}, headers=self.po_headers)
        assert resp.status_code == 200
        self.floor_id = resp.json()["id"]
        # room
        resp = client.post("/rooms", json={"name": "R1", "floorId": self.floor_id}, headers=self.po_headers)
        assert resp.status_code == 200
        self.room_id = resp.json()["id"]

    def test_po_can_crud_desk(self):
        # create desk
        resp = client.post("/desks", json={"roomId": self.room_id, "deskNumber": "D1"}, headers=self.po_headers)
        assert resp.status_code == 200
        desk_id = resp.json()["id"]

        # list
        resp2 = client.get("/desks", headers=self.po_headers)
        assert resp2.status_code == 200
        assert any(d["id"] == desk_id for d in resp2.json())

        # get
        resp3 = client.get(f"/desks/{desk_id}", headers=self.po_headers)
        assert resp3.status_code == 200

        # update
        resp4 = client.put(f"/desks/{desk_id}", json={"roomId": self.room_id, "deskNumber": "D2"}, headers=self.po_headers)
        assert resp4.status_code == 200
        assert resp4.json()["deskNumber"] == "D2"

        # delete
        resp5 = client.delete(f"/desks/{desk_id}", headers=self.po_headers)
        assert resp5.status_code == 200

    def test_self_service_limited(self):
        # create SS user
        u_id, u_token = create_user_and_login("ss_desk", "ss_desk@example.com", "pass")
        assign_role(u_id, "Self-Service", self.po_token)
        ss_headers = {"Authorization": f"Bearer {u_token}"}

        # create desk as PO to test read
        resp = client.post("/desks", json={"roomId": self.room_id, "deskNumber": "D3"}, headers=self.po_headers)
        assert resp.status_code == 200
        desk_id = resp.json()["id"]

        # self-service can list and get
        assert client.get("/desks", headers=ss_headers).status_code == 200
        assert client.get(f"/desks/{desk_id}", headers=ss_headers).status_code == 200

        # cannot create/update/delete
        assert client.post("/desks", json={"roomId": self.room_id, "deskNumber": "X"}, headers=ss_headers).status_code == 403
        assert client.put(f"/desks/{desk_id}", json={"roomId": self.room_id, "deskNumber": "Y"}, headers=ss_headers).status_code == 403
        assert client.delete(f"/desks/{desk_id}", headers=ss_headers).status_code == 403
