"""Agent endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_agent_user, get_current_admin_user
from app.crud.agent import crud_agent
from app.crud.delivery import crud_delivery
from app.crud.review import crud_review
from app.schemas.agent import AgentResponse, AgentUpdate, AgentLocationUpdate
from app.schemas.delivery import DeliveryResponse
from app.models.user import User
from app.models.review import Review
from app.services.delivery import delivery_service

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/profile", response_model=AgentResponse)
async def get_profile(
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Get my agent profile."""
    import logging
    logger = logging.getLogger(__name__)
    
    agent = crud_agent.get_by_user_id(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found")
    
    # Debug: Check if there are any reviews for this agent
    from sqlalchemy import func
    review_count = db.query(func.count()).select_from(Review).filter(Review.agent_id == agent.id).scalar()
    logger.info(f"Agent {agent.id} has {review_count} reviews")
    
    # Calculate average rating from reviews
    average_rating = crud_review.get_average_rating_by_agent(db, agent.id)
    logger.info(f"Calculated average rating for agent {agent.id}: {average_rating}")
    
    # Debug: Query reviews directly to see what's there
    reviews = db.query(Review.agent_rating).filter(Review.agent_id == agent.id).all()
    logger.info(f"Agent ratings: {[r[0] for r in reviews]}")
    
    # Convert agent to dict and add rating
    agent_data = {
        "id": agent.id,
        "user_id": agent.user_id,
        "agent_code": agent.agent_code,
        "status": agent.status,
        "assigned_area": agent.assigned_area,
        "vehicle_number": agent.vehicle_number,
        "current_latitude": agent.current_latitude,
        "current_longitude": agent.current_longitude,
        "total_deliveries": agent.total_deliveries,
        "total_earnings": agent.total_earnings,
        "available_for_delivery": agent.available_for_delivery,
        "rating": average_rating,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at,
    }
    
    return AgentResponse(**agent_data)


@router.put("/profile", response_model=AgentResponse)
async def update_profile(
    profile_data: AgentUpdate,
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Update my agent profile."""
    agent = crud_agent.get_by_user_id(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found")
    
    agent = crud_agent.update(db, agent, profile_data)
    return agent


@router.post("/location", response_model=AgentResponse)
async def update_location(
    location_data: AgentLocationUpdate,
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Update agent location (for tracking)."""
    agent = crud_agent.get_by_user_id(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found")
    
    agent = crud_agent.update_location(db, agent, location_data.latitude, location_data.longitude)
    return agent


@router.get("/deliveries/assigned", response_model=List[DeliveryResponse])
async def get_assigned_deliveries(
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Get assigned deliveries (agent)."""
    agent = crud_agent.get_by_user_id(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found")
    
    deliveries = crud_delivery.get_by_agent(db, agent.id)
    return deliveries


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get agent details (admin only)."""
    agent = crud_agent.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    # Calculate average rating from reviews
    average_rating = crud_review.get_average_rating_by_agent(db, agent.id)
    
    agent_data = {
        "id": agent.id,
        "user_id": agent.user_id,
        "agent_code": agent.agent_code,
        "status": agent.status,
        "assigned_area": agent.assigned_area,
        "vehicle_number": agent.vehicle_number,
        "current_latitude": agent.current_latitude,
        "current_longitude": agent.current_longitude,
        "total_deliveries": agent.total_deliveries,
        "total_earnings": agent.total_earnings,
        "available_for_delivery": agent.available_for_delivery,
        "rating": average_rating,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at,
    }
    
    return AgentResponse(**agent_data)


@router.get("/admin/all", response_model=List[AgentResponse])
async def get_all_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all agents (admin only)."""
    agents = crud_agent.get_multi(db, skip=skip, limit=limit)
    
    # Add ratings to each agent
    agents_with_ratings = []
    for agent in agents:
        average_rating = crud_review.get_average_rating_by_agent(db, agent.id)
        agent_data = {
            "id": agent.id,
            "user_id": agent.user_id,
            "agent_code": agent.agent_code,
            "status": agent.status,
            "assigned_area": agent.assigned_area,
            "vehicle_number": agent.vehicle_number,
            "current_latitude": agent.current_latitude,
            "current_longitude": agent.current_longitude,
            "total_deliveries": agent.total_deliveries,
            "total_earnings": agent.total_earnings,
            "available_for_delivery": agent.available_for_delivery,
            "rating": average_rating,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        }
        agents_with_ratings.append(AgentResponse(**agent_data))
    
    return agents_with_ratings


@router.get("/admin/available", response_model=List[AgentResponse])
async def get_available_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get available agents (admin only)."""
    agents = crud_agent.get_available_agents(db, skip=skip, limit=limit)
    
    # Add ratings to each agent
    agents_with_ratings = []
    for agent in agents:
        average_rating = crud_review.get_average_rating_by_agent(db, agent.id)
        agent_data = {
            "id": agent.id,
            "user_id": agent.user_id,
            "agent_code": agent.agent_code,
            "status": agent.status,
            "assigned_area": agent.assigned_area,
            "vehicle_number": agent.vehicle_number,
            "current_latitude": agent.current_latitude,
            "current_longitude": agent.current_longitude,
            "total_deliveries": agent.total_deliveries,
            "total_earnings": agent.total_earnings,
            "available_for_delivery": agent.available_for_delivery,
            "rating": average_rating,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        }
        agents_with_ratings.append(AgentResponse(**agent_data))
    
    return agents_with_ratings
