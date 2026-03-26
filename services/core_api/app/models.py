from typing import Optional, List
from pydantic import BaseModel

class IdModel(BaseModel):
    id: str

class Portfolio(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    landAreaSqm: Optional[float] = None
    customMetadata: Optional[dict] = None

class Building(BaseModel):
    id: Optional[str] = None
    portfolioId: Optional[str] = None
    name: str
    address: Optional[str] = None
    grossAreaSqm: Optional[float] = None
    customMetadata: Optional[dict] = None

class Floor(BaseModel):
    id: Optional[str] = None
    buildingId: str
    level: str
    grossAreaSqm: Optional[float] = None
    planFileUrl: Optional[str] = None

class Room(BaseModel):
    id: Optional[str] = None
    floorId: str
    name: str
    number: Optional[str] = None
    areaSqm: Optional[float] = None
    capacity: Optional[int] = None
    department: Optional[str] = None
    customMetadata: Optional[dict] = None

class Desk(BaseModel):
    id: Optional[str] = None
    roomId: str
    deskNumber: Optional[str] = None
    type: Optional[str] = "desk"  # desk, office, collaboration, huddle
    status: Optional[str] = "available"  # available, occupied, maintenance

class Employee(BaseModel):
    id: Optional[str]
    firstName: str
    lastName: str
    email: str
    phone: Optional[str]
    department: Optional[str]
    role: Optional[str]
    assignedRoomId: Optional[str]

class Occupancy(BaseModel):
    id: Optional[str]
    employeeId: str
    deskId: Optional[str]
    roomId: str
    assignmentDate: str  # ISO 8601 format
    releaseDate: Optional[str]  # ISO 8601 format
    status: Optional[str] = "assigned"  # assigned, unassigned, on_leave
    notes: Optional[str]

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
    id: Optional[str] = None
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
