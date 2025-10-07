from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Building:
    id: Optional[str]
    name: str
    address: Optional[str] = None
    grossAreaSqm: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Employee:
    id: Optional[str]
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    assignedRoomId: Optional[str] = None

@dataclass
class Asset:
    id: Optional[str]
    name: str
    assetTag: Optional[str] = None
    manufacturer: Optional[str] = None
    serialNumber: Optional[str] = None
    location: Optional[Dict[str, str]] = None
    warrantyExpiry: Optional[str] = None
    qrCodeUrl: Optional[str] = None

@dataclass
class WorkOrder:
    id: Optional[str]
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    requestedBy: Optional[str] = None
    assignedTo: Optional[str] = None
    assetId: Optional[str] = None
    location: Optional[Dict[str, str]] = None
    createdAt: Optional[str] = None
    dueDate: Optional[str] = None
    laborCost: Optional[float] = None
    partsCost: Optional[float] = None
