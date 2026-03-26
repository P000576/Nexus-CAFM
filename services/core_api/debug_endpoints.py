#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models_orm import UserORM, RoleORM, user_role_association
from app.auth import hash_password
from seed_rbac import seed_permissions, seed_roles
import uuid

client = TestClient(app)

# Initialize database
init_db()

# Setup RBAC
seed_permissions()
seed_roles()

def get_token(username, password):
    resp = client.post("/login", data={"username": username, "password": password})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return None

# Create test user if not exists
db = SessionLocal()
user = db.query(UserORM).filter(UserORM.username == "po_occ").first()
if not user:
    po_role = db.query(RoleORM).filter(RoleORM.name == "Process Owner").first()
    user = UserORM(
        id=str(uuid.uuid4()),
        username="po_occ",
        passwordHash=hash_password("pass"),
        licenseLevel="Process Owner",
        email="po@test.com"
    )
    if po_role:
        user.roles.append(po_role)
    db.add(user)
    db.commit()
db.close()

print('Testing endpoint chain...')
token = get_token("po_occ", "pass")
print('Token:', token[:20] + '...' if token else 'Failed')

# Verify user has roles
db = SessionLocal()
user = db.query(UserORM).filter(UserORM.username == "po_occ").first()
if user:
    print(f'User found: {user.username}, roles: {[r.name for r in user.roles]}')
else:
    print('User not found')
db.close()

if token:
    headers = {'Authorization': f'Bearer {token}'}
    import datetime
    ts = str(datetime.datetime.now().timestamp()).replace('.', '')
    
    # Create portfolio
    pname = f'Portfolio_{ts}'
    resp = client.post('/portfolios', json={'name': pname, 'description': 'Test', 'landAreaSqm': 1000.0}, headers=headers)
    print(f'Portfolio: {resp.status_code}', resp.json())
    if resp.status_code != 200:
        exit(1)
    portfolio_id = resp.json()["id"]
    
    # Create building
    bname = f'Building_{ts}'
    resp = client.post('/buildings', json={'name': bname, 'portfolioId': portfolio_id}, headers=headers)
    print(f'Building: {resp.status_code}', resp.json())
    if resp.status_code != 200:
        exit(1)
    building_id = resp.json()["id"]
    
    # Create floor
    resp = client.post('/floors', json={'level': f'Floor_{ts}', 'buildingId': building_id}, headers=headers)
    print(f'Floor: {resp.status_code}', resp.json())
else:
    print('Failed to get token')
