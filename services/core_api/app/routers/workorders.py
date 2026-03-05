from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import WorkOrder
from app.models_orm import WorkOrderORM
from app.database import get_db

router = APIRouter()

@router.post("/workorders", response_model=WorkOrder)
def create_workorder(w: WorkOrder, db: Session = Depends(get_db)):
    if not w.id:
        w.id = str(uuid4())
    
    db_workorder = WorkOrderORM(
        id=w.id,
        assetId=w.assetId,
        description=w.description,
        status=w.status or "New"
    )
    db.add(db_workorder)
    db.commit()
    db.refresh(db_workorder)
    return WorkOrder(**db_workorder.__dict__)

@router.get("/workorders", response_model=List[WorkOrder])
def list_workorders(db: Session = Depends(get_db)):
    workorders = db.query(WorkOrderORM).all()
    return [WorkOrder(**w.__dict__) for w in workorders]

@router.get("/workorders/{workorder_id}", response_model=WorkOrder)
def get_workorder(workorder_id: str, db: Session = Depends(get_db)):
    workorder = db.query(WorkOrderORM).filter(WorkOrderORM.id == workorder_id).first()
    if not workorder:
        raise HTTPException(status_code=404, detail="WorkOrder not found")
    return WorkOrder(**workorder.__dict__)

@router.put("/workorders/{workorder_id}", response_model=WorkOrder)
def update_workorder(workorder_id: str, w: WorkOrder, db: Session = Depends(get_db)):
    workorder = db.query(WorkOrderORM).filter(WorkOrderORM.id == workorder_id).first()
    if not workorder:
        raise HTTPException(status_code=404, detail="WorkOrder not found")
    
    workorder.assetId = w.assetId
    workorder.description = w.description
    workorder.status = w.status
    
    db.commit()
    db.refresh(workorder)
    return WorkOrder(**workorder.__dict__)

@router.delete("/workorders/{workorder_id}")
def delete_workorder(workorder_id: str, db: Session = Depends(get_db)):
    workorder = db.query(WorkOrderORM).filter(WorkOrderORM.id == workorder_id).first()
    if not workorder:
        raise HTTPException(status_code=404, detail="WorkOrder not found")
    db.delete(workorder)
    db.commit()
    return {"ok": True}
