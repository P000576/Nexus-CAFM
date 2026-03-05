from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4

from app.models import Room

router = APIRouter()

_rooms = {}

@router.post("/rooms", response_model=Room)
def create_room(r: Room):
    if not r.id:
        r.id = str(uuid4())
    _rooms[r.id] = r
    return r

@router.get("/rooms", response_model=List[Room])
def list_rooms():
    return list(_rooms.values())

@router.get("/rooms/{room_id}", response_model=Room)
def get_room(room_id: str):
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return _rooms[room_id]

@router.put("/rooms/{room_id}", response_model=Room)
def update_room(room_id: str, r: Room):
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    r.id = room_id
    _rooms[room_id] = r
    return r

@router.delete("/rooms/{room_id}")
def delete_room(room_id: str):
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    del _rooms[room_id]
    return {"ok": True}
