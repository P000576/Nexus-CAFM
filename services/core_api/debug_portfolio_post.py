from app.main import app
from fastapi.testclient import TestClient
from app.database import init_db
from app.models_orm import UserORM, RoleORM
from app.auth import hash_password
from seed_rbac import seed_permissions, seed_roles
from app.database import SessionLocal
import uuid

init_db()
seed_permissions()
seed_roles()
client = TestClient(app)

db = SessionLocal()
po_role = db.query(RoleORM).filter(RoleORM.name == "Process Owner").first()
user = UserORM(
    id=str(uuid.uuid4()),
    username='po_occ',
    email='po_occ@example.com',
    passwordHash=hash_password('pass'),
    firstName='Process',
    lastName='Owner',
    licenseLevel='Process Owner'
)
if po_role:
    user.roles.append(po_role)
db.add(user)
db.commit()
db.close()

r = client.post('/login', data={'username':'po_occ','password':'pass'})
print('login', r.status_code, r.text)
if r.status_code==200:
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    r2 = client.post('/portfolios', json={'name':'OccPortfolio'}, headers=headers)
    print('create portfolio', r2.status_code, r2.text)
else:
    print('cannot login')
