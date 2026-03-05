from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Permission, PermissionCreate
from app.models_orm import PermissionORM
from app.database import get_db

router = APIRouter()

@router.post("/permissions", response_model=Permission)
def create_permission(p: PermissionCreate, db: Session = Depends(get_db)):
    # Check if permission already exists
    existing = db.query(PermissionORM).filter(PermissionORM.name == p.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission name already exists")
    
    permission_id = str(uuid4())
    db_permission = PermissionORM(
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
    return Permission(**db_permission.__dict__)

@router.get("/permissions", response_model=List[Permission])
def list_permissions(module: str = None, action: str = None, db: Session = Depends(get_db)):
    query = db.query(PermissionORM)
    if module:
        query = query.filter(PermissionORM.module == module)
    if action:
        query = query.filter(PermissionORM.action == action)
    permissions = query.all()
    return [Permission(**p.__dict__) for p in permissions]

@router.get("/permissions/{permission_id}", response_model=Permission)
def get_permission(permission_id: str, db: Session = Depends(get_db)):
    permission = db.query(PermissionORM).filter(PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return Permission(**permission.__dict__)

@router.put("/permissions/{permission_id}", response_model=Permission)
def update_permission(permission_id: str, p: PermissionCreate, db: Session = Depends(get_db)):
    permission = db.query(PermissionORM).filter(PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    permission.name = p.name
    permission.description = p.description
    permission.module = p.module
    permission.action = p.action
    permission.fieldLevel = p.fieldLevel
    
    db.commit()
    db.refresh(permission)
    return Permission(**permission.__dict__)

@router.delete("/permissions/{permission_id}")
def delete_permission(permission_id: str, db: Session = Depends(get_db)):
    permission = db.query(PermissionORM).filter(PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(permission)
    db.commit()
    return {"ok": True}
