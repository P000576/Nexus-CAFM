from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4

from app.models import Employee

router = APIRouter()

_employees = {}

@router.post("/employees", response_model=Employee)
def create_employee(e: Employee):
    if not e.id:
        e.id = str(uuid4())
    _employees[e.id] = e
    return e

@router.get("/employees", response_model=List[Employee])
def list_employees():
    return list(_employees.values())

@router.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: str):
    if employee_id not in _employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _employees[employee_id]

@router.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: str, e: Employee):
    if employee_id not in _employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    e.id = employee_id
    _employees[employee_id] = e
    return e

@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: str):
    if employee_id not in _employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    del _employees[employee_id]
    return {"ok": True}
