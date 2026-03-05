from fastapi import FastAPI
from app.routers import buildings, floors, rooms, employees, assets, workorders
from app.database import init_db

app = FastAPI(
    title="Project Nexus Core API",
    version="0.1.0",
    description="Core platform backend for Project Nexus",
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(buildings.router)
app.include_router(floors.router)
app.include_router(rooms.router)
app.include_router(employees.router)
app.include_router(assets.router)
app.include_router(workorders.router)

@app.get("/")
def read_root():
    return {"message": "Project Nexus Core API", "docs": "/docs"}
