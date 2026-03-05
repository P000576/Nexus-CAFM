"""
Seed script to initialize example system settings for terminology customization.
This creates default terminology settings that can be customized by administrators.

Run after seed_rbac.py:
  python seed_rbac.py
  python seed_settings.py
"""

import uuid
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models_orm import SystemSettingORM


# Example settings for terminology customization and system configuration
EXAMPLE_SETTINGS = [
    # Terminology customization settings
    {
        "key": "terminology.building",
        "value": "Building",
        "description": "Display name for buildings (e.g., 'Site', 'Facility', 'Campus')"
    },
    {
        "key": "terminology.floor",
        "value": "Floor",
        "description": "Display name for floors (e.g., 'Level', 'Story')"
    },
    {
        "key": "terminology.room",
        "value": "Room",
        "description": "Display name for rooms (e.g., 'Space', 'Office')"
    },
    {
        "key": "terminology.employee",
        "value": "Employee",
        "description": "Display name for employees (e.g., 'Staff', 'User', 'Person')"
    },
    {
        "key": "terminology.asset",
        "value": "Asset",
        "description": "Display name for assets (e.g., 'Equipment', 'Item')"
    },
    {
        "key": "terminology.workorder",
        "value": "Work Order",
        "description": "Display name for work orders (e.g., 'Request', 'Ticket')"
    },
    
    # Company information settings
    {
        "key": "company.name",
        "value": "Your Company Name",
        "description": "Name of your organization"
    },
    {
        "key": "company.logo_url",
        "value": "https://example.com/logo.png",
        "description": "URL to company logo image"
    },
    
    # System notification settings
    {
        "key": "notifications.email_on_workorder_created",
        "value": "true",
        "description": "Send email when work order is created"
    },
    {
        "key": "notifications.email_on_workorder_assigned",
        "value": "true",
        "description": "Send email when work order is assigned"
    },
    {
        "key": "notifications.email_on_workorder_completed",
        "value": "true",
        "description": "Send email when work order is completed"
    },
    
    # System behavior settings
    {
        "key": "system.workorder_auto_assign_enabled",
        "value": "false",
        "description": "Automatically assign new work orders to available technicians"
    },
    {
        "key": "system.maintenance_schedule_frequency",
        "value": "monthly",
        "description": "Default frequency for maintenance tasks (daily, weekly, monthly, quarterly, annual)"
    },
    {
        "key": "system.default_asset_lifespan_years",
        "value": "10",
        "description": "Default expected lifespan of assets in years"
    },
    
    # Integration settings
    {
        "key": "integration.revit_sync_enabled",
        "value": "false",
        "description": "Enable automatic sync with Revit models"
    },
    {
        "key": "integration.calendar_integration_enabled",
        "value": "false",
        "description": "Enable calendar integration for scheduling"
    },
]


def seed_settings(db: Session):
    """Create or update example system settings."""
    created_count = 0
    updated_count = 0
    
    for setting_data in EXAMPLE_SETTINGS:
        # Check if setting already exists
        existing = db.query(SystemSettingORM).filter_by(key=setting_data["key"]).first()
        
        if existing:
            # Update existing setting if value is default
            if existing.value == existing.description or existing.value is None:
                existing.value = setting_data["value"]
                existing.description = setting_data["description"]
                db.commit()
                updated_count += 1
                print(f"Updated setting: {setting_data['key']}")
        else:
            # Create new setting
            new_setting = SystemSettingORM(
                id=str(uuid.uuid4()),
                key=setting_data["key"],
                value=setting_data["value"],
                description=setting_data["description"]
            )
            db.add(new_setting)
            created_count += 1
            print(f"Created setting: {setting_data['key']}")
    
    db.commit()
    print(f"\nSettings seeded: {created_count} created, {updated_count} updated")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    
    print("Seeding example system settings...")
    db = SessionLocal()
    try:
        seed_settings(db)
        print("\n[OK] System settings initialization complete!")
    finally:
        db.close()
