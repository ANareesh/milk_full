"""Location tracking endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_agent_user, get_current_admin_user, get_current_customer_user, get_current_user
from app.crud.location import crud_location
from app.crud.agent import crud_agent
from app.crud.delivery import crud_delivery
from app.crud.customer import crud_customer
from app.schemas.location import (
    LocationUpdate, LocationResponse, LocationHistoryResponse,
    AgentLocationResponse, AgentMapResponse
)
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/update", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def update_agent_location(
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Update agent's current location (Real-time GPS tracking)."""
    try:
        agent = crud_agent.get_by_user_id(db, current_user.id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent profile not found"
            )
        
        # Get active delivery if exists
        # Use existing method - gets first in_progress or pending delivery
        pending_deliveries = crud_delivery.get_agent_pending_deliveries(db, agent.id)
        active_delivery = pending_deliveries[0] if pending_deliveries else None
                
        # Create location record
        location = crud_location.create(
            db,
            agent.id,
            location_data,
            delivery_id=active_delivery.id if active_delivery else None
        )
        
        # Update agent's current position
        agent.current_latitude = location_data.latitude
        agent.current_longitude = location_data.longitude
        db.add(agent)
        db.commit()
        
        logger.info(f"Location updated for agent {agent.id}: {location_data.latitude}, {location_data.longitude}")
        
        return location
    except Exception as e:
        logger.error(f"Error updating location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update location"
        )


@router.get("/current", response_model=AgentLocationResponse)
async def get_current_location(
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Get agent's current location."""
    agent = crud_agent.get_by_user_id(db, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent profile not found"
        )
    
    location = crud_location.get_current_location(db, agent.id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No location data available"
        )
    
    return AgentLocationResponse(
        agent_id=agent.id,
        latitude=location.latitude,
        longitude=location.longitude,
        accuracy=location.accuracy,
        speed=location.speed,
        bearing=location.bearing,
        last_updated=location.timestamp
    )


@router.get("/history", response_model=LocationHistoryResponse)
async def get_location_history(
    hours: int = Query(24, ge=1, le=720),
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Get agent's location history."""
    agent = crud_agent.get_by_user_id(db, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent profile not found"
        )
    
    locations = crud_location.get_location_history(db, agent.id, hours)
    if not locations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No location history available"
        )
    
    total_distance = crud_location.calculate_total_distance(locations)
    average_speed = crud_location.calculate_average_speed(locations)
    
    return LocationHistoryResponse(
        locations=[LocationResponse.from_orm(loc) for loc in locations],
        total_distance=total_distance,
        average_speed=average_speed,
        start_time=locations[-1].timestamp,
        end_time=locations[0].timestamp
    )


@router.get("/delivery/{delivery_id}", response_model=List[LocationResponse])
async def get_delivery_route(
    delivery_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get complete route for a delivery."""
    delivery = crud_delivery.get(db, delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    locations = crud_location.get_delivery_route(db, delivery_id)
    return [LocationResponse.from_orm(loc) for loc in locations]


@router.get("/admin/agents-map", response_model=List[AgentMapResponse])
async def get_all_agents_map(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all agents' current locations for map display."""
    from app.crud.agent import crud_agent as agent_crud
    
    agents = agent_crud.get_multi(db, limit=1000)
    
    result = []
    for agent in agents:
        location = crud_location.get_current_location(db, agent.id)
        if location:
            # Get user name
            user = db.query(__import__('app.models.user', fromlist=['User']).User).filter(
                __import__('app.models.user', fromlist=['User']).User.id == agent.user_id
            ).first()
            
            result.append(AgentMapResponse(
                agent_id=agent.id,
                agent_name=user.full_name if user else f"Agent {agent.id}",
                latitude=location.latitude,
                longitude=location.longitude,
                status=str(agent.status),
                assigned_area=agent.assigned_area,
                current_delivery_id=location.delivery_id,
                last_updated=location.timestamp
            ))
    
    return result


@router.post("/calculate-distance")
async def calculate_distance(
    lat1: float = Query(...),
    lon1: float = Query(...),
    lat2: float = Query(...),
    lon2: float = Query(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Calculate distance between two coordinates."""
    distance = crud_location.calculate_distance(lat1, lon1, lat2, lon2)
    
    return {
        "distance_km": round(distance, 2),
        "distance_miles": round(distance * 0.621371, 2),
        "from": {"latitude": lat1, "longitude": lon1},
        "to": {"latitude": lat2, "longitude": lon2}
    }


@router.delete("/cleanup")
async def cleanup_old_locations(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete location history older than specified days."""
    try:
        crud_location.cleanup_old_locations(db, days)
        return {"message": f"Cleaned up locations older than {days} days"}
    except Exception as e:
        logger.error(f"Error cleaning up locations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup locations"
        )

@router.get("/map/admin/agents", response_model=dict)
async def get_admin_agents_map(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all agents on map for admin view."""
    try:
        agents_data = crud_location.get_agents_with_current_locations(db)
        stats = crud_location.get_map_statistics(db)
        
        # Count statuses
        agents_online = sum(1 for a in agents_data if a['status'] == 'active')
        agents_busy = sum(1 for a in agents_data if a['current_deliveries_count'] > 0)
        agents_on_break = sum(1 for a in agents_data if a['status'] == 'on_break')
        
        return {
            "success": True,
            "data": {
                "agents_online": agents_online,
                "agents_busy": agents_busy,
                "agents_on_break": agents_on_break,
                "total_deliveries_in_progress": stats['total_deliveries_in_progress'],
                "agent_markers": agents_data,
                "center_latitude": 28.7041,  # Default center
                "center_longitude": 77.1025,
                "zoom_level": 12,
                "timestamp": datetime.utcnow()
            },
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error fetching admin map data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch map data"
        )


@router.get("/map/customer/delivery-tracking")
async def get_customer_delivery_tracking(
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get delivery tracking for customer."""
    try:
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )
        
        delivery_data = crud_location.get_customer_active_delivery(db, customer.id)
        
        if not delivery_data:
            return {
                "success": True,
                "data": {
                    "has_active_delivery": False,
                    "delivery_marker": None,
                    "estimated_delivery_time": None,
                    "status_message": "No active delivery",
                    "timestamp": datetime.utcnow()
                }
            }
        
        status_message = {
            "pending": "Order confirmed, waiting for agent pickup",
            "in_progress": f"Agent {delivery_data['agent_name']} is on the way",
            "delivered": "Order delivered successfully"
        }.get(delivery_data['status'], "Unknown status")
        
        return {
            "success": True,
            "data": {
                "has_active_delivery": True,
                "delivery_marker": delivery_data,
                "estimated_delivery_time": delivery_data['estimated_arrival'],
                "status_message": status_message,
                "timestamp": datetime.utcnow()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching customer delivery tracking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch delivery tracking"
        )


@router.get("/map/delivery/{delivery_id}/route")
async def get_delivery_route_map(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get complete delivery route for map visualization."""
    try:
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery not found"
            )
        
        # Verify access
        if current_user.role == "customer":
            customer = crud_customer.get_by_user_id(db, current_user.id)
            if delivery.customer_id != customer.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this delivery"
                )
        
        route_points = crud_location.get_delivery_route(db, delivery_id)
        
        if not route_points:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No route data available"
            )
        
        agent = crud_agent.get(db, delivery.agent_id)
        agent_user = db.query(User).filter(User.id == agent.user_id).first() if agent else None
        
        start_point = route_points[0]
        end_point = route_points[-1]
        total_distance = crud_location.calculate_total_distance(route_points)
        average_speed = crud_location.calculate_average_speed(route_points)
        
        # Calculate duration
        if start_point and end_point:
            duration_seconds = (end_point.timestamp - start_point.timestamp).total_seconds()
            duration_minutes = int(duration_seconds / 60)
        else:
            duration_minutes = 0
        
        actual_duration = None
        if delivery.actual_delivery_date and delivery.pickup_time:
            actual_seconds = (delivery.actual_delivery_date - delivery.pickup_time).total_seconds()
            actual_duration = int(actual_seconds / 60)
        
        return {
            "success": True,
            "data": {
                "delivery_id": delivery_id,
                "agent_id": agent.id,
                "agent_name": agent_user.full_name if agent_user else "Unknown",
                "order_id": delivery.order_id,
                "start_point": {
                    "sequence": 1,
                    "latitude": start_point.latitude,
                    "longitude": start_point.longitude,
                    "timestamp": start_point.timestamp,
                    "speed": start_point.speed,
                    "accuracy": start_point.accuracy
                },
                "end_point": {
                    "sequence": len(route_points),
                    "latitude": end_point.latitude,
                    "longitude": end_point.longitude,
                    "timestamp": end_point.timestamp,
                    "speed": end_point.speed,
                    "accuracy": end_point.accuracy
                },
                "total_route_points": len(route_points),
                "total_distance_km": round(total_distance, 2),
                "average_speed_kmh": round(average_speed, 1),
                "estimated_duration_minutes": duration_minutes,
                "actual_duration_minutes": actual_duration,
                "route_points": [
                    {
                        "sequence": i + 1,
                        "latitude": pt.latitude,
                        "longitude": pt.longitude,
                        "timestamp": pt.timestamp,
                        "speed": pt.speed,
                        "accuracy": pt.accuracy
                    }
                    for i, pt in enumerate(route_points)
                ],
                "status": delivery.status,
                "created_at": delivery.created_at
            }
        }
    except Exception as e:
        logger.error(f"Error fetching delivery route: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch delivery route"
        )


@router.get("/map/stats")
async def get_map_statistics(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get map statistics."""
    try:
        stats = crud_location.get_map_statistics(db)
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error fetching map statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch map statistics"
        )