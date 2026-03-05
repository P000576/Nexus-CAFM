from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Role, RoleCreate
from app.models_orm import RoleORM
from app.database import get_db

router = APIRouter()

@router.post("/roles", response_model=Role)
def create_role(r: RoleCreate, db: Session = Depends(get_db)):
    # Check if role already exists
    existing = db.query(RoleORM).filter(RoleORM.name == r.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")
    
    role_id = str(uuid4())
    db_role = RoleORM(
        id=role_id,
        name=r.name,
        description=r.description
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return Role(**db_role.__dict__)

@router.get("/roles", response_model=List[Role])
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(RoleORM).all()
    return [Role(**r.__dict__) for r in roles]

@router.get("/roles/{role_id}", response_model=Role)
def get_role(role_id: str, db: Session = Depends(get_db)):
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return Role(**role.__dict__)

@router.put("/roles/{role_id}", response_model=Role)
def update_role(role_id: str, r: RoleCreate, db: Session = Depends(get_db)):
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role.name = r.name
    role.description = r.description
    
    db.commit()
    db.refresh(role)
    return Role(**role.__dict__)

@router.delete("/roles/{role_id}")
def delete_role(role_id: str, db: Session = Depends(get_db)):
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()
    return {"ok": True}

@router.post("/roles/{role_id}/permissions/{permission_id}")
def assign_permission_to_role(role_id: str, permission_id: str, db: Session = Depends(get_db)):
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    from app.models_orm import PermissionORM
    permission = db.query(PermissionORM).filter(PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
    
    return {"ok": True, "message": f"Permission {permission.name} assigned to role"}

@router.delete("/roles/{role_id}/permissions/{permission_id}")
def remove_permission_from_role(role_id: str, permission_id: str, db: Session = Depends(get_db)):
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    from app.models_orm import PermissionORM
    permission = db.query(PermissionORM).filter(PermissionORM.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.commit()
    
    return {"ok": True, "message": f"Permission {permission.name} removed from role"}
