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
