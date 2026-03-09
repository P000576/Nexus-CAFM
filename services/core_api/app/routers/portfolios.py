"""
Portfolio management endpoints (SP-02: Hierarchical Inventory)
Portfolios are the top-level container for buildings in the organizational hierarchy.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import Portfolio
from app.models_orm import PortfolioORM, BuildingORM, FloorORM, RoomORM, DeskORM, OccupancyORM
from app.database import get_db
from app.auth import require_permission, get_current_user

router = APIRouter()


@router.post("/portfolios", response_model=Portfolio, dependencies=[Depends(require_permission("portfolios", "create"))])
def create_portfolio(p: Portfolio, db: Session = Depends(get_db)):
    """Create a new portfolio"""
    existing = db.query(PortfolioORM).filter(PortfolioORM.name == p.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Portfolio name already exists")
    
    db_portfolio = PortfolioORM(
        id=str(uuid.uuid4()),
        name=p.name,
        description=p.description,
        landAreaSqm=p.landAreaSqm,
        customMetadata=str(p.customMetadata) if p.customMetadata else None
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return Portfolio(
        id=db_portfolio.id,
        name=db_portfolio.name,
        description=db_portfolio.description,
        landAreaSqm=db_portfolio.landAreaSqm,
        customMetadata=p.customMetadata
    )


@router.get("/portfolios", response_model=List[Portfolio], dependencies=[Depends(require_permission("portfolios", "read"))])
def list_portfolios(db: Session = Depends(get_db)):
    """List all portfolios"""
    portfolios = db.query(PortfolioORM).all()
    return [
        Portfolio(
            id=p.id,
            name=p.name,
            description=p.description,
            landAreaSqm=p.landAreaSqm,
            customMetadata={}
        ) for p in portfolios
    ]


@router.get("/portfolios/{portfolio_id}", response_model=Portfolio, dependencies=[Depends(require_permission("portfolios", "read"))])
def get_portfolio(portfolio_id: str, db: Session = Depends(get_db)):
    """Get a specific portfolio with its buildings"""
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return Portfolio(
        id=portfolio.id,
        name=portfolio.name,
        description=portfolio.description,
        landAreaSqm=portfolio.landAreaSqm,
        customMetadata={}
    )


@router.put("/portfolios/{portfolio_id}", response_model=Portfolio, dependencies=[Depends(require_permission("portfolios", "update"))])
def update_portfolio(portfolio_id: str, p: Portfolio, db: Session = Depends(get_db)):
    """Update a portfolio"""
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    portfolio.name = p.name
    portfolio.description = p.description
    portfolio.landAreaSqm = p.landAreaSqm
    if p.customMetadata:
        portfolio.customMetadata = str(p.customMetadata)
    
    db.commit()
    db.refresh(portfolio)
    
    return Portfolio(
        id=portfolio.id,
        name=portfolio.name,
        description=portfolio.description,
        landAreaSqm=portfolio.landAreaSqm,
        customMetadata={}
    )


@router.delete("/portfolios/{portfolio_id}", dependencies=[Depends(require_permission("portfolios", "delete"))])
def delete_portfolio(portfolio_id: str, db: Session = Depends(get_db)):
    """Delete a portfolio"""
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db.delete(portfolio)
    db.commit()
    return {"ok": True}


@router.get("/portfolios/{portfolio_id}/hierarchy", dependencies=[Depends(require_permission("portfolios", "read"))])
def get_hierarchy(portfolio_id: str, db: Session = Depends(get_db)):
    """Get full hierarchical view of portfolio: Portfolio → Buildings → Floors → Rooms → Desks → Occupancies"""
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    buildings = db.query(BuildingORM).filter(BuildingORM.portfolioId == portfolio_id).all()
    
    def build_floor_hierarchy(floor: FloorORM) -> Dict[str, Any]:
        rooms = db.query(RoomORM).filter(RoomORM.floorId == floor.id).all()
        return {
            "id": floor.id,
            "name": floor.name,
            "code": floor.code,
            "rooms": [build_room_hierarchy(room) for room in rooms]
        }
    
    def build_room_hierarchy(room: RoomORM) -> Dict[str, Any]:
        desks = db.query(DeskORM).filter(DeskORM.roomId == room.id).all()
        return {
            "id": room.id,
            "name": room.name,
            "code": room.code,
            "capacity": room.capacity,
            "desks": [build_desk_hierarchy(desk) for desk in desks]
        }
    
    def build_desk_hierarchy(desk: DeskORM) -> Dict[str, Any]:
        occupancies = db.query(OccupancyORM).filter(
            OccupancyORM.deskId == desk.id,
            OccupancyORM.status == "assigned"
        ).all()
        return {
            "id": desk.id,
            "deskNumber": desk.deskNumber,
            "type": desk.type,
            "status": desk.status,
            "occupancies": [
                {
                    "id": occ.id,
                    "employeeId": occ.employeeId,
                    "assignmentDate": occ.assignmentDate,
                    "releaseDate": occ.releaseDate,
                    "status": occ.status,
                    "notes": occ.notes
                } for occ in occupancies
            ]
        }
    
    def build_building_hierarchy(building: BuildingORM) -> Dict[str, Any]:
        floors = db.query(FloorORM).filter(FloorORM.buildingId == building.id).all()
        return {
            "id": building.id,
            "name": building.name,
            "code": building.code,
            "address": building.address,
            "floors": [build_floor_hierarchy(floor) for floor in floors]
        }
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "description": portfolio.description,
        "landAreaSqm": portfolio.landAreaSqm,
        "buildings": [build_building_hierarchy(building) for building in buildings]
    }

