from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4

from app.models import Floor

router = APIRouter()

_floors = {}

@router.post("/floors", response_model=Floor)
def create_floor(f: Floor):
    if not f.id:
        f.id = str(uuid4())
    _floors[f.id] = f
    return f

@router.get("/floors", response_model=List[Floor])
def list_floors():
    return list(_floors.values())

@router.get("/floors/{floor_id}", response_model=Floor)
def get_floor(floor_id: str):
    if floor_id not in _floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    return _floors[floor_id]

@router.put("/floors/{floor_id}", response_model=Floor)
def update_floor(floor_id: str, f: Floor):
    if floor_id not in _floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    f.id = floor_id
    _floors[floor_id] = f
    return f

@router.delete("/floors/{floor_id}")
def delete_floor(floor_id: str):
    if floor_id not in _floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    del _floors[floor_id]
    return {"ok": True}
