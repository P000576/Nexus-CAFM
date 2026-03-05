# RBAC Implementation Guide

## Overview
This document covers the Role-Based Access Control (RBAC) system implemented in the Project Nexus Core API (Epic 1 - ADM-01).

## Architecture

The RBAC system consists of four main components:

### 1. **Users** (`/users` endpoints)
- Stores system users with username, email, hashed password
- Each user can have multiple roles
- Four license levels: Self-Service, Work Process, Analysis, Process Owner
- Passwords hashed using bcrypt for security

### 2. **Roles** (`/roles` endpoints)
- Named role definitions (e.g., "Facility Manager", "Technician")
- Each role contains a set of permissions
- Default roles matching the four license levels are created during setup

### 3. **Permissions** (`/permissions` endpoints)
- Module-level and field-level access controls
- Format: `{module}:{action}` (e.g., `buildings:read`, `assets:update`)
- Modules: buildings, floors, rooms, employees, assets, workorders, users, roles, permissions
- Actions: create, read, update, delete

### 4. **Relationships**
```
User --[M:M]--> Role --[M:M]--> Permission
```

## Default License Levels

The system creates four default roles on initialization:

| License Level | Description | Key Permissions |
|---|---|---|
| **Self-Service** | Basic employee access | Room booking, service requests |
| **Work Process** | Operational staff | Manage assets and work orders |
| **Analysis** | Managers & analysts | Full read + analytics access |
| **Process Owner** | Administrators | Full CRUD on all resources + RBAC management |

## API Endpoints

### User Management
```
POST   /users                      # Create user
GET    /users                      # List all users
GET    /users/{user_id}            # Get user details
PUT    /users/{user_id}            # Update user
DELETE /users/{user_id}            # Delete user
POST   /users/{user_id}/roles/{role_id}    # Assign role
DELETE /users/{user_id}/roles/{role_id}    # Remove role
```

### Role Management
```
POST   /roles                      # Create role
GET    /roles                      # List all roles
GET    /roles/{role_id}            # Get role details
PUT    /roles/{role_id}            # Update role
DELETE /roles/{role_id}            # Delete role
POST   /roles/{role_id}/permissions/{permission_id}    # Assign permission
DELETE /roles/{role_id}/permissions/{permission_id}    # Remove permission
```

### Permission Management
```
POST   /permissions                # Create permission
GET    /permissions                # List permissions (query: module, action)
GET    /permissions/{permission_id} # Get permission
PUT    /permissions/{permission_id} # Update permission
DELETE /permissions/{permission_id} # Delete permission
```

## Getting Started

### 1. Install Dependencies
```bash
cd services/core_api
pip install -r requirements.txt
```

### 2. Seed RBAC Data
This initializes the four default roles and all permissions:
```bash
python seed_rbac.py
```

### 3. Start the API
```bash
uvicorn app.main:app --reload
```

### 4. Create a User
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jdoe",
    "email": "john.doe@company.com",
    "password": "securePassword123",
    "firstName": "John",
    "lastName": "Doe"
  }'
```

### 5. Assign a Role
```bash
curl -X POST http://localhost:8000/users/{user_id}/roles/{role_id}
```

## Security Considerations

- **Password Hashing**: Uses bcrypt with Passlib (industry standard)
- **Field-level permissions**: Extensible for fine-grained access control
- **No authentication middleware**: Currently API is open. Authentication (JWT/OAuth) to be Added in ADM-02
- **Module-level scoping**: Permissions are organized by module for easy policy management

## Next Steps (ADM-02)

- Implement JWT token-based authentication
- Add middleware to enforce permissions on all endpoints
- Implement field-level access control
- Add audit logging for role changes

## Database Schema

```
users (id, username, email, passwordHash, firstName, lastName, active, licenseLevel)
roles (id, name, description)
permissions (id, name, description, module, action, fieldLevel)
user_role (user_id, role_id) -- many-to-many
role_permission (role_id, permission_id) -- many-to-many
```
