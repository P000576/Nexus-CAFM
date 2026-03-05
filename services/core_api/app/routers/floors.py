from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Floor
from app.models_orm import FloorORM
from app.database import get_db
from app.auth import require_permission

router = APIRouter()

@router.post("/floors", response_model=Floor, dependencies=[Depends(require_permission("floors","create"))])
def create_floor(f: Floor, db: Session = Depends(get_db)):
    if not f.id:
        f.id = str(uuid4())
    
    db_floor = FloorORM(
        id=f.id,
        buildingId=f.buildingId,
        level=f.level,
        grossAreaSqm=f.grossAreaSqm,
        planFileUrl=f.planFileUrl
    )
    db.add(db_floor)
    db.commit()
    db.refresh(db_floor)
    return Floor(**db_floor.__dict__)

@router.get("/floors", response_model=List[Floor], dependencies=[Depends(require_permission("floors","read"))])
def list_floors(db: Session = Depends(get_db)):
    floors = db.query(FloorORM).all()
    return [Floor(**f.__dict__) for f in floors]

@router.get("/floors/{floor_id}", response_model=Floor, dependencies=[Depends(require_permission("floors","read"))])
def get_floor(floor_id: str, db: Session = Depends(get_db)):
    floor = db.query(FloorORM).filter(FloorORM.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return Floor(**floor.__dict__)

@router.put("/floors/{floor_id}", response_model=Floor, dependencies=[Depends(require_permission("floors","update"))])
def update_floor(floor_id: str, f: Floor, db: Session = Depends(get_db)):
    floor = db.query(FloorORM).filter(FloorORM.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    
    floor.buildingId = f.buildingId
    floor.level = f.level
    floor.grossAreaSqm = f.grossAreaSqm
    floor.planFileUrl = f.planFileUrl
    
    db.commit()
    db.refresh(floor)
    return Floor(**floor.__dict__)

@router.delete("/floors/{floor_id}", dependencies=[Depends(require_permission("floors","delete"))])
def delete_floor(floor_id: str, db: Session = Depends(get_db)):
    floor = db.query(FloorORM).filter(FloorORM.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    db.delete(floor)
    db.commit()
    return {"ok": True}
