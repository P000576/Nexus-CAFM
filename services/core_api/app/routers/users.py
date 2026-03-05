from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models import User, UserCreate
from app.models_orm import UserORM
from app.database import get_db

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/users", response_model=User)
def create_user(u: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(UserORM).filter(UserORM.username == u.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = db.query(UserORM).filter(UserORM.email == u.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_id = str(uuid4())
    db_user = UserORM(
        id=user_id,
        username=u.username,
        email=u.email,
        passwordHash=hash_password(u.password),
        firstName=u.firstName,
        lastName=u.lastName
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return User(**db_user.__dict__)

@router.get("/users", response_model=List[User])
def list_users(db: Session = Depends(get_db)):
    users = db.query(UserORM).all()
    return [User(**u.__dict__) for u in users]

@router.get("/users/{user_id}", response_model=User)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user.__dict__)

@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, u: UserCreate, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.username = u.username
    user.email = u.email
    user.firstName = u.firstName
    user.lastName = u.lastName
    user.passwordHash = hash_password(u.password)
    
    db.commit()
    db.refresh(user)
    return User(**user.__dict__)

@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}

@router.post("/users/{user_id}/roles/{role_id}")
def assign_role_to_user(user_id: str, role_id: str, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from app.models_orm import RoleORM
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    
    return {"ok": True, "message": f"Role {role.name} assigned to user"}

@router.delete("/users/{user_id}/roles/{role_id}")
def remove_role_from_user(user_id: str, role_id: str, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from app.models_orm import RoleORM
    role = db.query(RoleORM).filter(RoleORM.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
    
    return {"ok": True, "message": f"Role {role.name} removed from user"}
