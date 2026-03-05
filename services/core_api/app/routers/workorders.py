from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4

from app.models import WorkOrder

router = APIRouter()

_workorders = {}

@router.post("/workorders", response_model=WorkOrder)
def create_workorder(w: WorkOrder):
    if not w.id:
        w.id = str(uuid4())
    _workorders[w.id] = w
    return w

@router.get("/workorders", response_model=List[WorkOrder])
def list_workorders():
    return list(_workorders.values())

@router.get("/workorders/{workorder_id}", response_model=WorkOrder)
def get_workorder(workorder_id: str):
    if workorder_id not in _workorders:
        raise HTTPException(status_code=404, detail="WorkOrder not found")
    return _workorders[workorder_id]

@router.put("/workorders/{workorder_id}", response_model=WorkOrder)
def update_workorder(workorder_id: str, w: WorkOrder):
    if workorder_id not in _workorders:
        raise HTTPException(status_code=404, detail="WorkOrder not found")
    w.id = workorder_id
    _workorders[workorder_id] = w
    return w

@router.delete("/workorders/{workorder_id}")
def delete_workorder(workorder_id: str):
    if workorder_id not in _workorders:
        raise HTTPException(status_code=404, detail="WorkOrder not found")
    del _workorders[workorder_id]
    return {"ok": True}
