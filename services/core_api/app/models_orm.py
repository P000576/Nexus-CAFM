from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# Association tables for many-to-many relationships
user_role_association = Table(
    'user_role',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', String, ForeignKey('roles.id')),
)

role_permission_association = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', String, ForeignKey('roles.id')),
    Column('permission_id', String, ForeignKey('permissions.id')),
)

class BuildingORM(Base):
    __tablename__ = "buildings"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    grossAreaSqm = Column(Float, nullable=True)
    customMetadata = Column(String, nullable=True)  # JSON stored as string

    floors = relationship("FloorORM", back_populates="building")

class FloorORM(Base):
    __tablename__ = "floors"

    id = Column(String, primary_key=True)
    buildingId = Column(String, ForeignKey("buildings.id"), nullable=False)
    level = Column(String, nullable=False)
    grossAreaSqm = Column(Float, nullable=True)
    planFileUrl = Column(String, nullable=True)

    building = relationship("BuildingORM", back_populates="floors")
    rooms = relationship("RoomORM", back_populates="floor")

class RoomORM(Base):
    __tablename__ = "rooms"

    id = Column(String, primary_key=True)
    floorId = Column(String, ForeignKey("floors.id"), nullable=False)
    name = Column(String, nullable=False)
    number = Column(String, nullable=True)
    areaSqm = Column(Float, nullable=True)
    capacity = Column(Integer, nullable=True)
    department = Column(String, nullable=True)
    customMetadata = Column(String, nullable=True)

    floor = relationship("FloorORM", back_populates="rooms")

class EmployeeORM(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    department = Column(String, nullable=True)
    role = Column(String, nullable=True)
    assignedRoomId = Column(String, ForeignKey("rooms.id"), nullable=True)

class AssetORM(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    assetTag = Column(String, nullable=True, unique=True)
    manufacturer = Column(String, nullable=True)
    serialNumber = Column(String, nullable=True)

class WorkOrderORM(Base):
    __tablename__ = "workorders"

    id = Column(String, primary_key=True)
    assetId = Column(String, ForeignKey("assets.id"), nullable=True)
    description = Column(String, nullable=False)
    status = Column(String, default="New")
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemSettingORM(Base):
    __tablename__ = "system_settings"

    id = Column(String, primary_key=True)
    key = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)

class UserORM(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    passwordHash = Column(String, nullable=False)
    firstName = Column(String, nullable=True)
    lastName = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    licenseLevel = Column(String, default="Self-Service")  # Self-Service, Work Process, Analysis, Process Owner
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("RoleORM", secondary=user_role_association, back_populates="users")

class RoleORM(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("UserORM", secondary=user_role_association, back_populates="roles")
    permissions = relationship("PermissionORM", secondary=role_permission_association, back_populates="roles")

class PermissionORM(Base):
    __tablename__ = "permissions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    module = Column(String, nullable=False)  # e.g., "buildings", "employees", "assets"
    action = Column(String, nullable=False)  # e.g., "create", "read", "update", "delete"
    fieldLevel = Column(Boolean, default=False)  # if True, applicable at field level
    createdAt = Column(DateTime, default=datetime.utcnow)

    roles = relationship("RoleORM", secondary=role_permission_association, back_populates="permissions")
