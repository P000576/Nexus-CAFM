from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4

from app.models import Building

router = APIRouter()

# in-memory store for demo purposes
_buildings = {}

@router.post("/buildings", response_model=Building)
def create_building(b: Building):
    if not b.id:
        b.id = str(uuid4())
    _buildings[b.id] = b
    return b

@router.get("/buildings", response_model=List[Building])
def list_buildings():
    return list(_buildings.values())

@router.get("/buildings/{building_id}", response_model=Building)
def get_building(building_id: str):
    if building_id not in _buildings:
        raise HTTPException(status_code=404, detail="Building not found")
    return _buildings[building_id]

@router.put("/buildings/{building_id}", response_model=Building)
def update_building(building_id: str, b: Building):
    if building_id not in _buildings:
        raise HTTPException(status_code=404, detail="Building not found")
    b.id = building_id
    _buildings[building_id] = b
    return b

@router.delete("/buildings/{building_id}")
def delete_building(building_id: str):
    if building_id not in _buildings:
        raise HTTPException(status_code=404, detail="Building not found")
    del _buildings[building_id]
    return {"ok": True}
