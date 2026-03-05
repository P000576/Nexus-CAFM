"""
Tests for system settings endpoints with permission enforcement.
Validates that settings CRUD operations are properly secured with role-based access control.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal, init_db
from app.models_orm import UserORM, RoleORM, PermissionORM, SystemSettingORM, user_role_association
from app.auth import hash_password


# Initialize test database
def setup_module():
    """Initialize database and seed RBAC data before running tests."""
    init_db()
    db = SessionLocal()
    try:
        # Clear existing permissions, roles, and users
        db.query(PermissionORM).delete()
        db.query(RoleORM).delete()
        db.query(UserORM).delete()
        db.commit()
        
        # Create permissions
        print("Creating permissions...")
        permissions_config = {
            "settings": ["create", "read", "update", "delete"],
        }
        
        permissions_by_module = {}
        for module, actions in permissions_config.items():
            permissions_by_module[module] = {}
            for action in actions:
                perm = PermissionORM(
                    id=str(uuid.uuid4()),
                    name=f"{module}:{action}",
                    module=module,
                    action=action
                )
                db.add(perm)
                db.flush()
                permissions_by_module[module][action] = perm
        
        db.commit()
        
        # Create roles with permissions
        print("Creating roles...")
        
        # Self-Service role - read-only access to settings
        self_service_role = RoleORM(
            id=str(uuid.uuid4()),
            name="Self-Service",
            description="Self-Service user"
        )
        self_service_role.permissions.append(permissions_by_module["settings"]["read"])
        db.add(self_service_role)
        db.flush()
        
        # Process Owner role - full settings access
        process_owner_role = RoleORM(
            id=str(uuid.uuid4()),
            name="Process Owner",
            description="Administrator user"
        )
        for action in ["create", "read", "update", "delete"]:
            process_owner_role.permissions.append(permissions_by_module["settings"][action])
        db.add(process_owner_role)
        db.flush()
        
        db.commit()
        
        # Create test users
        print("Creating test users...")
        
        # Self-Service user - limited access
        self_service_user = UserORM(
            id=str(uuid.uuid4()),
            username="selfservice_user",
            email="selfservice@example.com",
            passwordHash=hash_password("selfservicepass"),
            licenseLevel="Self-Service"
        )
        db.add(self_service_user)
        db.flush()
        db.execute(
            user_role_association.insert().values(
                user_id=self_service_user.id,
                role_id=self_service_role.id
            )
        )
        
        # Process Owner user - full access
        admin_user = UserORM(
            id=str(uuid.uuid4()),
            username="admin_user",
            email="admin@example.com",
            passwordHash=hash_password("adminpass"),
            licenseLevel="Process Owner"
        )
        db.add(admin_user)
        db.flush()
        db.execute(
            user_role_association.insert().values(
                user_id=admin_user.id,
                role_id=process_owner_role.id
            )
        )
        
        db.commit()
        
        print("✓ RBAC data seeded for settings tests")
    finally:
        db.close()


client = TestClient(app)


def get_token(username: str, password: str) -> str:
    """Helper function to get JWT token for a user."""
    response = client.post(
        "/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestSettingsPermissions:
    """Test class for settings endpoints with permission enforcement."""
    
    @staticmethod
    def test_admin_can_create_setting():
        """Test that Process Owner role can create settings."""
        token = get_token("admin_user", "adminpass")
        headers = {"Authorization": f"Bearer {token}"}
        
        setting_data = {
            "key": "test.setting",
            "value": "test_value",
            "description": "Test setting"
        }
        
        response = client.post(
            "/settings",
            json=setting_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.setting"
        assert data["value"] == "test_value"
        print("✓ Admin can create settings")
    
    @staticmethod
    def test_self_service_cannot_create_setting():
        """Test that Self-Service role cannot create settings."""
        token = get_token("selfservice_user", "selfservicepass")
        headers = {"Authorization": f"Bearer {token}"}
        
        setting_data = {
            "key": "unauthorized.setting",
            "value": "test_value",
            "description": "Unauthorized attempt"
        }
        
        response = client.post(
            "/settings",
            json=setting_data,
            headers=headers
        )
        
        assert response.status_code == 403
        print("✓ Self-Service user denied from creating settings")
    
    @staticmethod
    def test_admin_can_read_settings():
        """Test that Process Owner can read settings."""
        token = get_token("admin_user", "adminpass")
        headers = {"Authorization": f"Bearer {token}"}
        
        # First create a setting
        setting_data = {
            "key": "company.name",
            "value": "Test Company",
            "description": "Test company setting"
        }
        create_response = client.post(
            "/settings",
            json=setting_data,
            headers=headers
        )
        assert create_response.status_code == 200
        
        # Then read it
        response = client.get(
            "/settings",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(s["key"] == "company.name" for s in data)
        print("✓ Admin can read settings list")
    
    @staticmethod
    def test_self_service_can_read_settings():
        """Test that Self-Service role can read settings."""
        token = get_token("selfservice_user", "selfservicepass")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            "/settings",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print("✓ Self-Service user can read settings")
    
    @staticmethod
    def test_admin_can_update_setting():
        """Test that Process Owner can update settings."""
        admin_token = get_token("admin_user", "adminpass")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a setting first
        setting_data = {
            "key": "terminology.building",
            "value": "Building",
            "description": "Building terminology"
        }
        create_response = client.post(
            "/settings",
            json=setting_data,
            headers=admin_headers
        )
        assert create_response.status_code == 200
        setting_id = create_response.json()["id"]
        
        # Update the setting
        updated_data = {
            "key": "terminology.building",
            "value": "Site",
            "description": "Updated to Site"
        }
        response = client.put(
            f"/settings/{setting_id}",
            json=updated_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == "Site"
        print("✓ Admin can update settings")
    
    @staticmethod
    def test_self_service_cannot_update_setting():
        """Test that Self-Service role cannot update settings."""
        admin_token = get_token("admin_user", "adminpass")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        self_service_token = get_token("selfservice_user", "selfservicepass")
        self_service_headers = {"Authorization": f"Bearer {self_service_token}"}
        
        # Create a setting as admin
        setting_data = {
            "key": "test.update.denied",
            "value": "original",
            "description": "Test update denied"
        }
        create_response = client.post(
            "/settings",
            json=setting_data,
            headers=admin_headers
        )
        assert create_response.status_code == 200
        setting_id = create_response.json()["id"]
        
        # Try to update as self-service user
        updated_data = {
            "key": "test.update.denied",
            "value": "modified",
            "description": "Unauthorized update"
        }
        response = client.put(
            f"/settings/{setting_id}",
            json=updated_data,
            headers=self_service_headers
        )
        
        assert response.status_code == 403
        print("✓ Self-Service user denied from updating settings")
    
    @staticmethod
    def test_admin_can_delete_setting():
        """Test that Process Owner can delete settings."""
        admin_token = get_token("admin_user", "adminpass")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a setting first
        setting_data = {
            "key": "test.delete",
            "value": "to_delete",
            "description": "Setting to delete"
        }
        create_response = client.post(
            "/settings",
            json=setting_data,
            headers=admin_headers
        )
        assert create_response.status_code == 200
        setting_id = create_response.json()["id"]
        
        # Delete the setting
        response = client.delete(
            f"/settings/{setting_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        print("✓ Admin can delete settings")
    
    @staticmethod
    def test_self_service_cannot_delete_setting():
        """Test that Self-Service role cannot delete settings."""
        admin_token = get_token("admin_user", "adminpass")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        self_service_token = get_token("selfservice_user", "selfservicepass")
        self_service_headers = {"Authorization": f"Bearer {self_service_token}"}
        
        # Create a setting as admin
        setting_data = {
            "key": "test.delete.denied",
            "value": "protected",
            "description": "Delete denied"
        }
        create_response = client.post(
            "/settings",
            json=setting_data,
            headers=admin_headers
        )
        assert create_response.status_code == 200
        setting_id = create_response.json()["id"]
        
        # Try to delete as self-service user
        response = client.delete(
            f"/settings/{setting_id}",
            headers=self_service_headers
        )
        
        assert response.status_code == 403
        print("✓ Self-Service user denied from deleting settings")
    
    @staticmethod
    def test_unauthenticated_cannot_access_settings():
        """Test that unauthenticated requests are rejected."""
        # Try to access settings without token
        response = client.get("/settings")
        assert response.status_code == 401  # 401 Unauthorized for missing auth
        
        # Try to create settings without token
        response = client.post(
            "/settings",
            json={"key": "test", "value": "test"}
        )
        assert response.status_code == 401  # 401 Unauthorized for missing auth
        print("✓ Unauthenticated users denied from settings endpoints")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
