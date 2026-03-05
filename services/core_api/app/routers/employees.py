from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models import Employee
from app.models_orm import EmployeeORM
from app.database import get_db

router = APIRouter()

@router.post("/employees", response_model=Employee)
def create_employee(e: Employee, db: Session = Depends(get_db)):
    if not e.id:
        e.id = str(uuid4())
    
    db_employee = EmployeeORM(
        id=e.id,
        firstName=e.firstName,
        lastName=e.lastName,
        email=e.email,
        phone=e.phone,
        department=e.department,
        role=e.role,
        assignedRoomId=e.assignedRoomId
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return Employee(**db_employee.__dict__)

@router.get("/employees", response_model=List[Employee])
def list_employees(db: Session = Depends(get_db)):
    employees = db.query(EmployeeORM).all()
    return [Employee(**e.__dict__) for e in employees]

@router.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(EmployeeORM).filter(EmployeeORM.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return Employee(**employee.__dict__)

@router.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: str, e: Employee, db: Session = Depends(get_db)):
    employee = db.query(EmployeeORM).filter(EmployeeORM.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.firstName = e.firstName
    employee.lastName = e.lastName
    employee.email = e.email
    employee.phone = e.phone
    employee.department = e.department
    employee.role = e.role
    employee.assignedRoomId = e.assignedRoomId
    
    db.commit()
    db.refresh(employee)
    return Employee(**employee.__dict__)

@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(EmployeeORM).filter(EmployeeORM.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"ok": True}
