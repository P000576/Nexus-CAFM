from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4

from app.models import Asset

router = APIRouter()

_assets = {}

@router.post("/assets", response_model=Asset)
def create_asset(a: Asset):
    if not a.id:
        a.id = str(uuid4())
    _assets[a.id] = a
    return a

@router.get("/assets", response_model=List[Asset])
def list_assets():
    return list(_assets.values())

@router.get("/assets/{asset_id}", response_model=Asset)
def get_asset(asset_id: str):
    if asset_id not in _assets:
        raise HTTPException(status_code=404, detail="Asset not found")
    return _assets[asset_id]

@router.put("/assets/{asset_id}", response_model=Asset)
def update_asset(asset_id: str, a: Asset):
    if asset_id not in _assets:
        raise HTTPException(status_code=404, detail="Asset not found")
    a.id = asset_id
    _assets[asset_id] = a
    return a

@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: str):
    if asset_id not in _assets:
        raise HTTPException(status_code=404, detail="Asset not found")
    del _assets[asset_id]
    return {"ok": True}
