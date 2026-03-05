from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from app.models import SystemSetting
from app.models_orm import SystemSettingORM
from app.database import get_db
from app.auth import require_permission, get_current_user

router = APIRouter()

@router.post("/settings", response_model=SystemSetting, dependencies=[Depends(require_permission("settings","create"))])
def create_setting(s: SystemSetting, db: Session = Depends(get_db)):
    existing = db.query(SystemSettingORM).filter(SystemSettingORM.key == s.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Setting key already exists")
    db_setting = SystemSettingORM(key=s.key, value=s.value, description=s.description)
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return s

@router.get("/settings", response_model=List[SystemSetting], dependencies=[Depends(require_permission("settings","read"))])
def list_settings(db: Session = Depends(get_db)):
    items = db.query(SystemSettingORM).all()
    return [SystemSetting(key=i.key, value=i.value, description=i.description) for i in items]

@router.put("/settings/{key}", response_model=SystemSetting, dependencies=[Depends(require_permission("settings","update"))])
def update_setting(key: str, s: SystemSetting, db: Session = Depends(get_db)):
    setting = db.query(SystemSettingORM).filter(SystemSettingORM.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting.value = s.value
    setting.description = s.description
    db.commit()
    db.refresh(setting)
    return SystemSetting(key=setting.key, value=setting.value, description=setting.description)

@router.delete("/settings/{key}", dependencies=[Depends(require_permission("settings","delete"))])
def delete_setting(key: str, db: Session = Depends(get_db)):
    setting = db.query(SystemSettingORM).filter(SystemSettingORM.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    db.commit()
    return {"ok": True}
