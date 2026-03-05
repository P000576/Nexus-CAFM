from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Room
from app.models_orm import RoomORM
from app.database import get_db
from app.auth import require_permission

router = APIRouter()

@router.post("/rooms", response_model=Room, dependencies=[Depends(require_permission("rooms","create"))])
def create_room(r: Room, db: Session = Depends(get_db)):
    if not r.id:
        r.id = str(uuid4())
    
    db_room = RoomORM(
        id=r.id,
        floorId=r.floorId,
        name=r.name,
        number=r.number,
        areaSqm=r.areaSqm,
        capacity=r.capacity,
        department=r.department,
        metadata=str(r.metadata) if r.metadata else None
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return Room(**db_room.__dict__)

@router.get("/rooms", response_model=List[Room], dependencies=[Depends(require_permission("rooms","read"))])
def list_rooms(db: Session = Depends(get_db)):
    rooms = db.query(RoomORM).all()
    return [Room(**r.__dict__) for r in rooms]

@router.get("/rooms/{room_id}", response_model=Room, dependencies=[Depends(require_permission("rooms","read"))])
def get_room(room_id: str, db: Session = Depends(get_db)):
    room = db.query(RoomORM).filter(RoomORM.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return Room(**room.__dict__)

@router.put("/rooms/{room_id}", response_model=Room, dependencies=[Depends(require_permission("rooms","update"))])
def update_room(room_id: str, r: Room, db: Session = Depends(get_db)):
    room = db.query(RoomORM).filter(RoomORM.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room.floorId = r.floorId
    room.name = r.name
    room.number = r.number
    room.areaSqm = r.areaSqm
    room.capacity = r.capacity
    room.department = r.department
    room.metadata = str(r.metadata) if r.metadata else None
    
    db.commit()
    db.refresh(room)
    return Room(**room.__dict__)

@router.delete("/rooms/{room_id}", dependencies=[Depends(require_permission("rooms","delete"))])
def delete_room(room_id: str, db: Session = Depends(get_db)):
    room = db.query(RoomORM).filter(RoomORM.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    db.delete(room)
    db.commit()
    return {"ok": True}
