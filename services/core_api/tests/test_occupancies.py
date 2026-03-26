"""
Tests for occupancy endpoints with permission enforcement (SP-04).
"""

# pyright: reportMissingImports=false

from fastapi.testclient import TestClient
from datetime import datetime
import os
import sys
import io
import uuid

# ensure the application package can be imported when tests are
# executed from the workspace root (which may not be the project
# directory).  This mirrors how pytest adds the project root to
# sys.path when running inside services/core_api.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import init_db, SessionLocal
from seed_rbac import seed_permissions, seed_roles
from app.models_orm import UserORM, RoleORM, PermissionORM, user_role_association
from app.auth import hash_password

client = TestClient(app)


def setup_module(module):
    """Initialize database and create test users with roles."""
    init_db()
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(PermissionORM).delete()
        db.query(RoleORM).delete()
        db.query(UserORM).delete()
        db.commit()

        # Seed permissions and roles
        seed_permissions()
        seed_roles()

        # Get roles
        po_role = db.query(RoleORM).filter(RoleORM.name == "Process Owner").first()
        ss_role = db.query(RoleORM).filter(RoleORM.name == "Self-Service").first()
        assert po_role and ss_role

        # Create test users
        po_user = UserORM(
            id=str(uuid.uuid4()),
            username="po_occ",
            email="po_occ@example.com",
            passwordHash=hash_password("pass"),
            firstName="Process",
            lastName="Owner",
            licenseLevel="Process Owner"
        )
        db.add(po_user)
        db.flush()
        db.execute(
            user_role_association.insert().values(
                user_id=po_user.id,
                role_id=po_role.id
            )
        )

        ss_user = UserORM(
            id=str(uuid.uuid4()),
            username="ss_occ",
            email="ss_occ@example.com",
            passwordHash=hash_password("pass"),
            firstName="Self",
            lastName="Service",
            licenseLevel="Self-Service"
        )
        db.add(ss_user)
        db.flush()
        db.execute(
            user_role_association.insert().values(
                user_id=ss_user.id,
                role_id=ss_role.id
            )
        )

        db.commit()
        print("[OK] Test users created for occupancy tests")
    finally:
        db.close()


def get_token(username: str, password: str) -> str:
    """Helper function to get JWT token for a user."""
    response = client.post(
        "/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


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
        # Use pre-created users from setup_module
        self.po_token = get_token("po_occ", "pass")
        self.po_headers = {"Authorization": f"Bearer {self.po_token}"}

        # create hierarchy and desk
        resp = client.post("/portfolios", json={"name": "OccPortfolio"}, headers=self.po_headers)
        assert resp.status_code == 200, f"Portfolio creation failed: {resp.status_code} {resp.text}"
        self.portfolio_id = resp.json()["id"]
        resp = client.post("/buildings", json={"name": "B", "portfolioId": self.portfolio_id}, headers=self.po_headers)
        self.building_id = resp.json()["id"]
        resp = client.post("/floors", json={"level": "F", "buildingId": self.building_id}, headers=self.po_headers)
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
        # Use pre-created self-service user
        ss_token = get_token("ss_occ", "pass")
        ss_headers = {"Authorization": f"Bearer {ss_token}"}

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

    def test_bulk_import(self):
        # create another employee for bulk import
        resp = client.post("/employees", json={
            "firstName": "Emp",
            "lastName": "Two",
            "email": "emp2@example.com"
        }, headers=self.po_headers)
        emp2_id = resp.json()["id"]

        # create CSV content
        csv_content = """EmployeeID,DeskID,RoomID,AssignmentDate,Status,Notes
{},{},{},2024-01-01T00:00:00,assigned,Imported from CSV
{},,{},2024-01-02T00:00:00,assigned,Room only assignment
""".format(self.employee_id, self.desk_id, self.room_id, emp2_id, self.room_id)

        # upload CSV
        files = {"file": ("occupancies.csv", csv_content, "text/csv")}
        resp = client.post("/occupancies/bulk-import", files=files, headers=self.po_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["successful_imports"] == 2
        assert len(result["errors"]) == 0

        # verify occupancies were created
        resp2 = client.get("/occupancies", headers=self.po_headers)
        assert resp2.status_code == 200
        occs = resp2.json()
        assert len(occs) >= 2  # at least the two imported

        # check specific assignments
        emp1_occ = next((o for o in occs if o["employeeId"] == self.employee_id), None)
        assert emp1_occ is not None
        assert emp1_occ["deskId"] == self.desk_id
        assert emp1_occ["notes"] == "Imported from CSV"

        emp2_occ = next((o for o in occs if o["employeeId"] == emp2_id), None)
        assert emp2_occ is not None
        assert emp2_occ["deskId"] is None  # room only
        assert emp2_occ["notes"] == "Room only assignment"

    def test_bulk_import_invalid_file_format(self):
        # test non-CSV file
        files = {"file": ("occupancies.txt", "not csv content", "text/plain")}
        resp = client.post("/occupancies/bulk-import", files=files, headers=self.po_headers)
        assert resp.status_code == 400
        assert "File must be a CSV" in resp.json()["detail"]

    def test_bulk_import_missing_required_fields(self):
        # CSV with missing EmployeeID and RoomID
        csv_content = """EmployeeID,DeskID,RoomID,AssignmentDate,Status,Notes
,,{},2024-01-01T00:00:00,assigned,Missing employee
{},,2024-01-02T00:00:00,assigned,Missing room
""".format(self.room_id, self.employee_id)

        files = {"file": ("occupancies.csv", csv_content, "text/csv")}
        resp = client.post("/occupancies/bulk-import", files=files, headers=self.po_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["successful_imports"] == 0
        assert len(result["errors"]) == 2
        assert any("EmployeeID and RoomID are required" in error for error in result["errors"])

    def test_bulk_import_nonexistent_entities(self):
        # CSV with invalid UUIDs
        csv_content = """EmployeeID,DeskID,RoomID,AssignmentDate,Status,Notes
invalid-employee-id,{},{},2024-01-01T00:00:00,assigned,Invalid employee
{},{},invalid-room-id,2024-01-02T00:00:00,assigned,Invalid room
{},invalid-desk-id,{},2024-01-03T00:00:00,assigned,Invalid desk
""".format(self.desk_id, self.room_id, self.employee_id, self.room_id, self.employee_id, self.room_id)

        files = {"file": ("occupancies.csv", csv_content, "text/csv")}
        resp = client.post("/occupancies/bulk-import", files=files, headers=self.po_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["successful_imports"] == 0
        assert len(result["errors"]) == 3
        assert any("Employee" in error and "not found" in error for error in result["errors"])
        assert any("Room" in error and "not found" in error for error in result["errors"])
        assert any("Desk" in error and "not found" in error for error in result["errors"])

    def test_bulk_import_duplicate_active_assignment(self):
        # first create an active occupancy for employee
        resp = client.post("/occupancies", json={
            "employeeId": self.employee_id,
            "deskId": self.desk_id,
            "roomId": self.room_id
        }, headers=self.po_headers)
        assert resp.status_code == 200

        # now try to import another active assignment for same employee
        csv_content = """EmployeeID,DeskID,RoomID,AssignmentDate,Status,Notes
{},{},{},2024-01-01T00:00:00,assigned,Duplicate assignment
""".format(self.employee_id, self.desk_id, self.room_id)

        files = {"file": ("occupancies.csv", csv_content, "text/csv")}
        resp = client.post("/occupancies/bulk-import", files=files, headers=self.po_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["successful_imports"] == 0
        assert len(result["errors"]) == 1
        assert "already has an active occupancy assignment" in result["errors"][0]

    def test_bulk_import_invalid_date_format(self):
        # CSV with invalid date
        csv_content = """EmployeeID,DeskID,RoomID,AssignmentDate,Status,Notes
{},{},{},invalid-date,assigned,Bad date
""".format(self.employee_id, self.desk_id, self.room_id)

        files = {"file": ("occupancies.csv", csv_content, "text/csv")}
        resp = client.post("/occupancies/bulk-import", files=files, headers=self.po_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["successful_imports"] == 0
        assert len(result["errors"]) == 1
        assert "Invalid AssignmentDate format" in result["errors"][0]

    def test_bulk_import_mixed_success_and_errors(self):
        # create another employee for successful import
        resp = client.post("/employees", json={
            "firstName": "Emp",
            "lastName": "Three",
            "email": "emp3@example.com"
        }, headers=self.po_headers)
        emp3_id = resp.json()["id"]

        # CSV with mix of valid and invalid rows
        csv_content = """EmployeeID,DeskID,RoomID,AssignmentDate,Status,Notes
{},{},{},2024-01-01T00:00:00,assigned,Valid row 1
invalid-emp,{},{},2024-01-02T00:00:00,assigned,Invalid employee
{},{},invalid-room,2024-01-03T00:00:00,assigned,Invalid room
{},{},{},invalid-date,assigned,Invalid date
{},{},{},2024-01-05T00:00:00,assigned,Valid row 2
""".format(self.employee_id, self.desk_id, self.room_id, self.room_id, self.employee_id, self.room_id, self.employee_id, self.desk_id, self.room_id, emp3_id, self.room_id)

        files = {"file": ("occupancies.csv", csv_content, "text/csv")}
        resp = client.post("/occupancies/bulk-import", files=files, headers=self.po_headers)
        assert resp.status_code == 200
        result = resp.json()
        assert result["successful_imports"] == 2  # two valid rows
        assert len(result["errors"]) == 3  # three invalid rows
        assert result["total_rows_processed"] == 5

        # verify the successful imports were actually created
        resp2 = client.get("/occupancies", headers=self.po_headers)
        assert resp2.status_code == 200
        occs = resp2.json()
        valid_emps = [o for o in occs if o["employeeId"] in [self.employee_id, emp3_id]]
        assert len(valid_emps) == 2

    def test_bulk_import_permission_denied(self):
        # Use pre-created self-service user
        ss_token = get_token("ss_occ", "pass")
        ss_headers = {"Authorization": f"Bearer {ss_token}"}

        csv_content = """EmployeeID,DeskID,RoomID,AssignmentDate,Status,Notes
{},{},{},2024-01-01T00:00:00,assigned,Test
""".format(self.employee_id, self.desk_id, self.room_id)

        files = {"file": ("occupancies.csv", csv_content, "text/csv")}
        resp = client.post("/occupancies/bulk-import", files=files, headers=ss_headers)
        assert resp.status_code == 403
