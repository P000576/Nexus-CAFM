"""
Tests for occupancy endpoints with permission enforcement (SP-04).
"""

# pyright: reportMissingImports=false

from fastapi.testclient import TestClient
from datetime import datetime
import os
import sys

# ensure the application package can be imported when tests are
# executed from the workspace root (which may not be the project
# directory).  This mirrors how pytest adds the project root to
# sys.path when running inside services/core_api.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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


class TestOccupancyPermissions:
    def setup_class(self):
        # create process owner for setup tasks
        self.po_id, self.po_token = create_user_and_login("po_occ", "po_occ@example.com", "pass")
        assign_role(self.po_id, "Process Owner", self.po_token)
        self.po_headers = {"Authorization": f"Bearer {self.po_token}"}

        # create hierarchy and desk
        resp = client.post("/portfolios", json={"name": "OccPortfolio"}, headers=self.po_headers)
        self.portfolio_id = resp.json()["id"]
        resp = client.post("/buildings", json={"name": "B", "portfolioId": self.portfolio_id}, headers=self.po_headers)
        self.building_id = resp.json()["id"]
        resp = client.post("/floors", json={"name": "F", "buildingId": self.building_id}, headers=self.po_headers)
        self.floor_id = resp.json()["id"]
        resp = client.post("/rooms", json={"name": "R", "floorId": self.floor_id}, headers=self.po_headers)
        self.room_id = resp.json()["id"]
        resp = client.post("/desks", json={"roomId": self.room_id, "deskNumber": "D"}, headers=self.po_headers)
        self.desk_id = resp.json()["id"]

        # create an employee
        resp = client.post("/employees", json={
            "firstName": "Emp",
            "lastName": "One",
            "email": "emp1@example.com"
        }, headers=self.po_headers)
        self.employee_id = resp.json()["id"]

    def test_po_can_manage_occupancy(self):
        # create occupancy
        occ_data = {
            "employeeId": self.employee_id,
            "deskId": self.desk_id,
            "roomId": self.room_id,
            "assignmentDate": datetime.now().isoformat(),
            "status": "assigned"
        }
        resp = client.post("/occupancies", json=occ_data, headers=self.po_headers)
        assert resp.status_code == 200
        occ_id = resp.json()["id"]

        # duplicate active assignment should fail
        resp_dup = client.post("/occupancies", json=occ_data, headers=self.po_headers)
        assert resp_dup.status_code == 400

        # list/filter
        resp2 = client.get(f"/occupancies?employee_id={self.employee_id}", headers=self.po_headers)
        assert resp2.status_code == 200
        assert any(o["id"] == occ_id for o in resp2.json())

        # get
        resp3 = client.get(f"/occupancies/{occ_id}", headers=self.po_headers)
        assert resp3.status_code == 200

        # update (release)
        resp4 = client.put(f"/occupancies/{occ_id}", json={"employeeId": self.employee_id, "roomId": self.room_id, "status": "released", "releaseDate": datetime.now().isoformat()}, headers=self.po_headers)
        assert resp4.status_code == 200
        assert resp4.json()["status"] == "released"

        # delete
        resp5 = client.delete(f"/occupancies/{occ_id}", headers=self.po_headers)
        assert resp5.status_code == 200

    def test_self_service_limited(self):
        u_id, u_token = create_user_and_login("ss_occ", "ss_occ@example.com", "pass")
        assign_role(u_id, "Self-Service", self.po_token)
        ss_headers = {"Authorization": f"Bearer {u_token}"}

        # create new occupancy for visibility
        resp = client.post("/occupancies", json={
            "employeeId": self.employee_id,
            "deskId": self.desk_id,
            "roomId": self.room_id
        }, headers=self.po_headers)
        occ_id = resp.json()["id"]

        # self-service can list and get
        assert client.get("/occupancies", headers=ss_headers).status_code == 200
        assert client.get(f"/occupancies/{occ_id}", headers=ss_headers).status_code == 200

        # cannot create/update/delete
        assert client.post("/occupancies", json={"employeeId": self.employee_id, "roomId": self.room_id}, headers=ss_headers).status_code == 403
        assert client.put(f"/occupancies/{occ_id}", json={"employeeId": self.employee_id, "roomId": self.room_id}, headers=ss_headers).status_code == 403
        assert client.delete(f"/occupancies/{occ_id}", headers=ss_headers).status_code == 403
