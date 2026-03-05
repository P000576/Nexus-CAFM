from fastapi import APIRouter, HTTPException, Depends
import uuid
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
    db_setting = SystemSettingORM(
        id=str(uuid.uuid4()),
        key=s.key, 
        value=s.value, 
        description=s.description
    )
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return SystemSetting(id=db_setting.id, key=db_setting.key, value=db_setting.value, description=db_setting.description)

@router.get("/settings", response_model=List[SystemSetting], dependencies=[Depends(require_permission("settings","read"))])
def list_settings(db: Session = Depends(get_db)):
    items = db.query(SystemSettingORM).all()
    return [SystemSetting(id=i.id, key=i.key, value=i.value, description=i.description) for i in items]

@router.put("/settings/{setting_id}", response_model=SystemSetting, dependencies=[Depends(require_permission("settings","update"))])
def update_setting(setting_id: str, s: SystemSetting, db: Session = Depends(get_db)):
    setting = db.query(SystemSettingORM).filter(SystemSettingORM.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting.value = s.value
    setting.description = s.description
    db.commit()
    db.refresh(setting)
    return SystemSetting(id=setting.id, key=setting.key, value=setting.value, description=setting.description)

@router.delete("/settings/{setting_id}", dependencies=[Depends(require_permission("settings","delete"))])
def delete_setting(setting_id: str, db: Session = Depends(get_db)):
    setting = db.query(SystemSettingORM).filter(SystemSettingORM.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    db.commit()
    return {"ok": True}
