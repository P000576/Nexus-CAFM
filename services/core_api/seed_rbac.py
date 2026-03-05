#!/usr/bin/env python
"""
Script to initialize default roles and permissions for Project Nexus RBAC.
This sets up the four default license levels and basic permission structure.
"""

from sqlalchemy.orm import Session
from uuid import uuid4
from app.database import engine, SessionLocal, init_db
from app.models_orm import Base, RoleORM, PermissionORM

def seed_permissions():
    """Create default permissions for all modules"""
    db = SessionLocal()
    try:
        # Clear existing permissions
        db.query(PermissionORM).delete()
        db.commit()
        
        modules = ["buildings", "floors", "rooms", "employees", "assets", "workorders", "users", "roles", "permissions", "settings"]
        actions = ["create", "read", "update", "delete"]
        
        permissions = []
        for module in modules:
            for action in actions:
                permission = PermissionORM(
                    id=str(uuid4()),
                    name=f"{module}:{action}",
                    description=f"Permission to {action} {module}",
                    module=module,
                    action=action,
                    fieldLevel=False
                )
                permissions.append(permission)
        
        db.add_all(permissions)
        db.commit()
        print(f"✓ Created {len(permissions)} default permissions")
        
    finally:
        db.close()

def seed_roles():
    """Create the four default license levels/roles"""
    db = SessionLocal()
    try:
        # Clear existing roles
        db.query(RoleORM).delete()
        db.commit()
        
        roles_config = [
            {
                "name": "Self-Service",
                "description": "Basic employee access - desk/room booking, service requests",
                "permissions": ["rooms:read", "employees:read", "workorders:create"]
            },
            {
                "name": "Work Process",
                "description": "Operational staff - maintain assets, manage work orders",
                "permissions": [
                    "buildings:read", "floors:read", "rooms:read", "rooms:update",
                    "employees:read", "assets:read", "assets:update",
                    "workorders:read", "workorders:create", "workorders:update"
                ]
            },
            {
                "name": "Analysis",
                "description": "Analyst and manager - full read access and reporting",
                "permissions": [
                    "buildings:read", "buildings:update",
                    "floors:read", "floors:update",
                    "rooms:read", "rooms:update",
                    "employees:read", "employees:update",
                    "assets:read", "assets:update",
                    "workorders:read", "workorders:update"
                ]
            },
            {
                "name": "Process Owner",
                "description": "Administrator - full access to all modules and RBAC",
                "permissions": [
                    "buildings:create", "buildings:read", "buildings:update", "buildings:delete",
                    "floors:create", "floors:read", "floors:update", "floors:delete",
                    "rooms:create", "rooms:read", "rooms:update", "rooms:delete",
                    "employees:create", "employees:read", "employees:update", "employees:delete",
                    "assets:create", "assets:read", "assets:update", "assets:delete",
                    "workorders:create", "workorders:read", "workorders:update", "workorders:delete",
                    "users:create", "users:read", "users:update", "users:delete",
                    "roles:create", "roles:read", "roles:update", "roles:delete",
                    "permissions:create", "permissions:read", "permissions:update", "permissions:delete",
                    "settings:create", "settings:read", "settings:update", "settings:delete"
                ]
            }
        ]
        
        for role_config in roles_config:
            role = RoleORM(
                id=str(uuid4()),
                name=role_config["name"],
                description=role_config["description"]
            )
            
            # Assign permissions to role
            for perm_name in role_config["permissions"]:
                permission = db.query(PermissionORM).filter(PermissionORM.name == perm_name).first()
                if permission:
                    role.permissions.append(permission)
            
            db.add(role)
        
        db.commit()
        print(f"✓ Created {len(roles_config)} default roles (license levels)")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✓ Database schema created\n")
    
    print("Seeding default permissions...")
    seed_permissions()
    
    print("Seeding default roles...")
    seed_roles()
    
    print("\n✅ RBAC setup complete!")
    print("\nDefault License Levels:")
    print("  1. Self-Service - Basic employee access")
    print("  2. Work Process - Operational staff")
    print("  3. Analysis - Analysts and managers")
    print("  4. Process Owner - Full administrator access")
