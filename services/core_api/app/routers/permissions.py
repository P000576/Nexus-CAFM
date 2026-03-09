from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter()

@router.post("/permissions", response_model=models.Permission)
def create_permission(p: models.PermissionCreate, db: Session = Depends(get_db)):
    # Check if permission already exists
    existing = db.query(models.PermissionORM).filter(models.PermissionORM.name == p.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission name already exists")
    
    permission_id = str(uuid4())
    db_permission = models.PermissionORM(
        id=permission_id,
        name=p.name,
        description=p.description,
        module=p.module,
        action=p.action,
        fieldLevel=p.fieldLevel
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return models.Permission(**db_permission.__dict__)

@router.get("/permissions", response_model=List[models.Permission])

def list_permissions(module: Optional[str] = None, action: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.PermissionORM)
    if module:
        query = query.filter(models.PermissionORM.module == module)
    if action:
        query = query.filter(models.PermissionORM.action == action)
    permissions = query.all()
    return [models.Permission(**p.__dict__) for p in permissions]

@router.get("/permissions/{permission_id}", response_model=models.Permission)
def get_permission(permission_id: str, db: Session = Depends(get_db)):
    permission = db.query(models.PermissionORM).filter(models.PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return models.Permission(**permission.__dict__)

@router.put("/permissions/{permission_id}", response_model=models.Permission)
def update_permission(permission_id: str, p: models.PermissionCreate, db: Session = Depends(get_db)):
    permission = db.query(models.PermissionORM).filter(models.PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    permission.name = p.name
    permission.description = p.description
    permission.module = p.module
    permission.action = p.action
    permission.fieldLevel = p.fieldLevel
    
    db.commit()
    db.refresh(permission)
    return models.Permission(**permission.__dict__)

@router.delete("/permissions/{permission_id}")
def delete_permission(permission_id: str, db: Session = Depends(get_db)):
    permission = db.query(models.PermissionORM).filter(models.PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(permission)
    db.commit()
    return {"ok": True}
