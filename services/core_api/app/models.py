from typing import Optional, List
from pydantic import BaseModel

class IdModel(BaseModel):
    id: str

class Building(BaseModel):
    id: Optional[str]
    name: str
    address: Optional[str]
    grossAreaSqm: Optional[float]
    metadata: Optional[dict] = {}

class Floor(BaseModel):
    id: Optional[str]
    buildingId: str
    level: str
    grossAreaSqm: Optional[float]
    planFileUrl: Optional[str]

class Room(BaseModel):
    id: Optional[str]
    floorId: str
    name: str
    number: Optional[str]
    areaSqm: Optional[float]
    capacity: Optional[int]
    department: Optional[str]
    metadata: Optional[dict] = {}

class Employee(BaseModel):
    id: Optional[str]
    firstName: str
    lastName: str
    email: str
    phone: Optional[str]
    department: Optional[str]
    role: Optional[str]
    assignedRoomId: Optional[str]

class Asset(BaseModel):
    id: Optional[str]
    name: str
    assetTag: Optional[str]
    manufacturer: Optional[str]
    serialNumber: Optional[str]

class WorkOrder(BaseModel):
    id: Optional[str]
    assetId: Optional[str]
    description: str
    status: Optional[str] = "New"

class Permission(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    module: str  # "buildings", "employees", "assets", etc
    action: str  # "create", "read", "update", "delete"
    fieldLevel: Optional[bool] = False

class Role(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    permissions: Optional[List[Permission]] = []

class User(BaseModel):
    id: Optional[str]
    username: str
    email: str
    firstName: Optional[str]
    lastName: Optional[str]
    active: Optional[bool] = True
    licenseLevel: Optional[str] = "Self-Service"  # Self-Service, Work Process, Analysis, Process Owner
    roles: Optional[List[Role]] = []

class SystemSetting(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    firstName: Optional[str]
    lastName: Optional[str]

class RoleCreate(BaseModel):
    name: str
    description: Optional[str]

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str]
    module: str
    action: str
    fieldLevel: Optional[bool] = False
