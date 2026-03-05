from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Asset
from app.models_orm import AssetORM
from app.database import get_db
from app.auth import require_permission

router = APIRouter()

@router.post("/assets", response_model=Asset, dependencies=[Depends(require_permission("assets","create"))])
def create_asset(a: Asset, db: Session = Depends(get_db)):
    if not a.id:
        a.id = str(uuid4())
    
    db_asset = AssetORM(
        id=a.id,
        name=a.name,
        assetTag=a.assetTag,
        manufacturer=a.manufacturer,
        serialNumber=a.serialNumber
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return Asset(**db_asset.__dict__)

@router.get("/assets", response_model=List[Asset], dependencies=[Depends(require_permission("assets","read"))])
def list_assets(db: Session = Depends(get_db)):
    assets = db.query(AssetORM).all()
    return [Asset(**a.__dict__) for a in assets]

@router.get("/assets/{asset_id}", response_model=Asset, dependencies=[Depends(require_permission("assets","read"))])
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(AssetORM).filter(AssetORM.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return Asset(**asset.__dict__)

@router.put("/assets/{asset_id}", response_model=Asset, dependencies=[Depends(require_permission("assets","update"))])
def update_asset(asset_id: str, a: Asset, db: Session = Depends(get_db)):
    asset = db.query(AssetORM).filter(AssetORM.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset.name = a.name
    asset.assetTag = a.assetTag
    asset.manufacturer = a.manufacturer
    asset.serialNumber = a.serialNumber
    
    db.commit()
    db.refresh(asset)
    return Asset(**asset.__dict__)

@router.delete("/assets/{asset_id}", dependencies=[Depends(require_permission("assets","delete"))])
def delete_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(AssetORM).filter(AssetORM.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return {"ok": True}
