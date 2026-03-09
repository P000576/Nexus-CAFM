"""
Occupancy management endpoints (SP-04)
Track employee-to-desk and employee-to-room assignments for space utilization.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Occupancy
from app.models_orm import OccupancyORM, EmployeeORM, DeskORM, RoomORM
from app.database import get_db
from app.auth import require_permission

router = APIRouter()


@router.post("/occupancies", response_model=Occupancy, dependencies=[Depends(require_permission("occupancies", "create"))])
def create_occupancy(occ: Occupancy, db: Session = Depends(get_db)):
    """Create an occupancy assignment (employee to desk/room)"""
    # Validate employee exists
    employee = db.query(EmployeeORM).filter(EmployeeORM.id == occ.employeeId).first()
    if not employee:
        raise HTTPException(status_code=400, detail="Employee not found")
    
    # Validate desk if provided
    if occ.deskId:
        desk = db.query(DeskORM).filter(DeskORM.id == occ.deskId).first()
        if not desk:
            raise HTTPException(status_code=400, detail="Desk not found")
    
    # Validate room exists
    room = db.query(RoomORM).filter(RoomORM.id == occ.roomId).first()
    if not room:
        raise HTTPException(status_code=400, detail="Room not found")
    
    # Check for duplicate active assignment for this employee
    existing = db.query(OccupancyORM).filter(
        OccupancyORM.employeeId == occ.employeeId,
        OccupancyORM.status == "assigned",
        OccupancyORM.releaseDate == None
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee already has an active occupancy assignment")
    
    db_occ = OccupancyORM(
        id=str(uuid.uuid4()),
        employeeId=occ.employeeId,
        deskId=occ.deskId,
        roomId=occ.roomId,
        assignmentDate=occ.assignmentDate or datetime.now().isoformat(),
        releaseDate=occ.releaseDate,
        status=occ.status or "assigned",
        notes=occ.notes
    )
    db.add(db_occ)
    db.commit()
    db.refresh(db_occ)
    
    return Occupancy(
        id=db_occ.id,
        employeeId=db_occ.employeeId,
        deskId=db_occ.deskId,
        roomId=db_occ.roomId,
        assignmentDate=db_occ.assignmentDate,
        releaseDate=db_occ.releaseDate,
        status=db_occ.status,
        notes=db_occ.notes
    )


@router.get("/occupancies", response_model=List[Occupancy], dependencies=[Depends(require_permission("occupancies", "read"))])
def list_occupancies(
    employee_id: Optional[str] = None,
    desk_id: Optional[str] = None,
    room_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List occupancies with optional filtering"""
    query = db.query(OccupancyORM)
    
    if employee_id:
        query = query.filter(OccupancyORM.employeeId == employee_id)
    if desk_id:
        query = query.filter(OccupancyORM.deskId == desk_id)
    if room_id:
        query = query.filter(OccupancyORM.roomId == room_id)
    if status:
        query = query.filter(OccupancyORM.status == status)
    
    occupancies = query.all()
    return [
        Occupancy(
            id=occ.id,
            employeeId=occ.employeeId,
            deskId=occ.deskId,
            roomId=occ.roomId,
            assignmentDate=occ.assignmentDate,
            releaseDate=occ.releaseDate,
            status=occ.status,
            notes=occ.notes
        ) for occ in occupancies
    ]


@router.get("/occupancies/{occupancy_id}", response_model=Occupancy, dependencies=[Depends(require_permission("occupancies", "read"))])
def get_occupancy(occupancy_id: str, db: Session = Depends(get_db)):
    """Get a specific occupancy assignment"""
    occupancy = db.query(OccupancyORM).filter(OccupancyORM.id == occupancy_id).first()
    if not occupancy:
        raise HTTPException(status_code=404, detail="Occupancy not found")
    
    return Occupancy(
        id=occupancy.id,
        employeeId=occupancy.employeeId,
        deskId=occupancy.deskId,
        roomId=occupancy.roomId,
        assignmentDate=occupancy.assignmentDate,
        releaseDate=occupancy.releaseDate,
        status=occupancy.status,
        notes=occupancy.notes
    )


@router.put("/occupancies/{occupancy_id}", response_model=Occupancy, dependencies=[Depends(require_permission("occupancies", "update"))])
def update_occupancy(occupancy_id: str, occ: Occupancy, db: Session = Depends(get_db)):
    """Update an occupancy assignment"""
    occupancy = db.query(OccupancyORM).filter(OccupancyORM.id == occupancy_id).first()
    if not occupancy:
        raise HTTPException(status_code=404, detail="Occupancy not found")
    
    # Validate desk if being updated
    if occ.deskId and occ.deskId != occupancy.deskId:
        desk = db.query(DeskORM).filter(DeskORM.id == occ.deskId).first()
        if not desk:
            raise HTTPException(status_code=400, detail="Desk not found")
    
    # Validate room if being updated
    if occ.roomId != occupancy.roomId:
        room = db.query(RoomORM).filter(RoomORM.id == occ.roomId).first()
        if not room:
            raise HTTPException(status_code=400, detail="Room not found")
    
    occupancy.deskId = occ.deskId if occ.deskId else occupancy.deskId
    occupancy.roomId = occ.roomId
    occupancy.status = occ.status or occupancy.status
    occupancy.releaseDate = occ.releaseDate
    occupancy.notes = occ.notes or occupancy.notes
    
    db.commit()
    db.refresh(occupancy)
    
    return Occupancy(
        id=occupancy.id,
        employeeId=occupancy.employeeId,
        deskId=occupancy.deskId,
        roomId=occupancy.roomId,
        assignmentDate=occupancy.assignmentDate,
        releaseDate=occupancy.releaseDate,
        status=occupancy.status,
        notes=occupancy.notes
    )


@router.delete("/occupancies/{occupancy_id}", dependencies=[Depends(require_permission("occupancies", "delete"))])
def delete_occupancy(occupancy_id: str, db: Session = Depends(get_db)):
    """Delete an occupancy assignment"""
    occupancy = db.query(OccupancyORM).filter(OccupancyORM.id == occupancy_id).first()
    if not occupancy:
        raise HTTPException(status_code=404, detail="Occupancy not found")
    
    db.delete(occupancy)
    db.commit()
    return {"ok": True}
