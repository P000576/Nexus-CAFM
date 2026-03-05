from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Building
from app.models_orm import BuildingORM
from app.database import get_db
from app.auth import require_permission

router = APIRouter()

@router.post("/buildings", response_model=Building, dependencies=[Depends(require_permission("buildings","create"))])
def create_building(b: Building, db: Session = Depends(get_db)):
    if not b.id:
        b.id = str(uuid4())
    
    db_building = BuildingORM(
        id=b.id,
        name=b.name,
        address=b.address,
        grossAreaSqm=b.grossAreaSqm,
        metadata=str(b.metadata) if b.metadata else None
    )
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return Building(**db_building.__dict__)

@router.get("/buildings", response_model=List[Building], dependencies=[Depends(require_permission("buildings","read"))])
def list_buildings(db: Session = Depends(get_db)):
    buildings = db.query(BuildingORM).all()
    return [Building(**b.__dict__) for b in buildings]

@router.get("/buildings/{building_id}", response_model=Building, dependencies=[Depends(require_permission("buildings","read"))])
def get_building(building_id: str, db: Session = Depends(get_db)):
    building = db.query(BuildingORM).filter(BuildingORM.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return Building(**building.__dict__)

@router.put("/buildings/{building_id}", response_model=Building, dependencies=[Depends(require_permission("buildings","update"))])
def update_building(building_id: str, b: Building, db: Session = Depends(get_db)):
    building = db.query(BuildingORM).filter(BuildingORM.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    building.name = b.name
    building.address = b.address
    building.grossAreaSqm = b.grossAreaSqm
    building.metadata = str(b.metadata) if b.metadata else None
    
    db.commit()
    db.refresh(building)
    return Building(**building.__dict__)

@router.delete("/buildings/{building_id}", dependencies=[Depends(require_permission("buildings","delete"))])
def delete_building(building_id: str, db: Session = Depends(get_db)):
    building = db.query(BuildingORM).filter(BuildingORM.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    db.delete(building)
    db.commit()
    return {"ok": True}
