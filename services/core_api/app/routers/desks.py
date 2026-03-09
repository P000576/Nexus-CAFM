"""
Desk/Workstation management endpoints (SP-02, SP-04)
Individual workstations within rooms for occupancy management.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Desk
from app.models_orm import DeskORM, RoomORM
from app.database import get_db
from app.auth import require_permission

router = APIRouter()


@router.post("/desks", response_model=Desk, dependencies=[Depends(require_permission("desks", "create"))])
def create_desk(d: Desk, db: Session = Depends(get_db)):
    """Create a new desk/workstation"""
    room = db.query(RoomORM).filter(RoomORM.id == d.roomId).first()
    if not room:
        raise HTTPException(status_code=400, detail="Room not found")
    
    db_desk = DeskORM(
        id=str(uuid.uuid4()),
        roomId=d.roomId,
        deskNumber=d.deskNumber,
        type=d.type or "desk",
        status=d.status or "available"
    )
    db.add(db_desk)
    db.commit()
    db.refresh(db_desk)
    
    return Desk(
        id=db_desk.id,
        roomId=db_desk.roomId,
        deskNumber=db_desk.deskNumber,
        type=db_desk.type,
        status=db_desk.status
    )


@router.get("/desks", response_model=List[Desk], dependencies=[Depends(require_permission("desks", "read"))])
def list_desks(room_id: Optional[str] = None, db: Session = Depends(get_db)):
    """List all desks, optionally filtered by room"""
    query = db.query(DeskORM)
    if room_id:
        query = query.filter(DeskORM.roomId == room_id)
    
    desks = query.all()
    return [
        Desk(
            id=d.id,
            roomId=d.roomId,
            deskNumber=d.deskNumber,
            type=d.type,
            status=d.status
        ) for d in desks
    ]


@router.get("/desks/{desk_id}", response_model=Desk, dependencies=[Depends(require_permission("desks", "read"))])
def get_desk(desk_id: str, db: Session = Depends(get_db)):
    """Get a specific desk"""
    desk = db.query(DeskORM).filter(DeskORM.id == desk_id).first()
    if not desk:
        raise HTTPException(status_code=404, detail="Desk not found")
    
    return Desk(
        id=desk.id,
        roomId=desk.roomId,
        deskNumber=desk.deskNumber,
        type=desk.type,
        status=desk.status
    )


@router.put("/desks/{desk_id}", response_model=Desk, dependencies=[Depends(require_permission("desks", "update"))])
def update_desk(desk_id: str, d: Desk, db: Session = Depends(get_db)):
    """Update a desk"""
    desk = db.query(DeskORM).filter(DeskORM.id == desk_id).first()
    if not desk:
        raise HTTPException(status_code=404, detail="Desk not found")
    
    desk.deskNumber = d.deskNumber
    desk.type = d.type or desk.type
    desk.status = d.status or desk.status
    
    db.commit()
    db.refresh(desk)
    
    return Desk(
        id=desk.id,
        roomId=desk.roomId,
        deskNumber=desk.deskNumber,
        type=desk.type,
        status=desk.status
    )


@router.delete("/desks/{desk_id}", dependencies=[Depends(require_permission("desks", "delete"))])
def delete_desk(desk_id: str, db: Session = Depends(get_db)):
    """Delete a desk"""
    desk = db.query(DeskORM).filter(DeskORM.id == desk_id).first()
    if not desk:
        raise HTTPException(status_code=404, detail="Desk not found")
    
    db.delete(desk)
    db.commit()
    return {"ok": True}
