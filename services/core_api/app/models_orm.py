from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class BuildingORM(Base):
    __tablename__ = "buildings"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    grossAreaSqm = Column(Float, nullable=True)
    metadata = Column(String, nullable=True)  # JSON stored as string

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
    metadata = Column(String, nullable=True)

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
