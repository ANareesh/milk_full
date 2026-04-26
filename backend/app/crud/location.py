"""Location CRUD operations."""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt

from app.models.agent_location import AgentLocation
from app.schemas.location import LocationUpdate


class CRUDLocation:
    """CRUD operations for agent locations."""

    @staticmethod
    def create(db: Session, agent_id: int, location_data: LocationUpdate, delivery_id: Optional[int] = None) -> AgentLocation:
        """Create new location record."""
        location = AgentLocation(
            agent_id=agent_id,
            delivery_id=delivery_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            accuracy=location_data.accuracy,
            speed=location_data.speed,
            bearing=location_data.bearing,
            address=location_data.address,
            is_active=1
        )
        
        # Mark previous location as history
        db.query(AgentLocation).filter(
            AgentLocation.agent_id == agent_id,
            AgentLocation.is_active == 1
        ).update({AgentLocation.is_active: 0})
        
        db.add(location)
        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def get_current_location(db: Session, agent_id: int) -> Optional[AgentLocation]:
        """Get agent's current location."""
        return db.query(AgentLocation).filter(
            AgentLocation.agent_id == agent_id,
            AgentLocation.is_active == 1
        ).order_by(desc(AgentLocation.timestamp)).first()

    @staticmethod
    def get_location_history(
        db: Session,
        agent_id: int,
        hours: int = 24,
        limit: int = 100
    ) -> List[AgentLocation]:
        """Get location history for agent."""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(AgentLocation).filter(
            AgentLocation.agent_id == agent_id,
            AgentLocation.created_at >= start_time
        ).order_by(desc(AgentLocation.timestamp)).limit(limit).all()

    @staticmethod
    def get_delivery_route(db: Session, delivery_id: int) -> List[AgentLocation]:
        """Get complete route for a delivery."""
        return db.query(AgentLocation).filter(
            AgentLocation.delivery_id == delivery_id
        ).order_by(AgentLocation.timestamp).all()

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth's radius in kilometers
        
        return c * r

    @staticmethod
    def calculate_total_distance(locations: List[AgentLocation]) -> float:
        """Calculate total distance traveled."""
        if len(locations) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(locations) - 1):
            dist = CRUDLocation.calculate_distance(
                locations[i].latitude,
                locations[i].longitude,
                locations[i+1].latitude,
                locations[i+1].longitude
            )
            total_distance += dist
        
        return total_distance

    @staticmethod
    def calculate_average_speed(locations: List[AgentLocation]) -> float:
        """Calculate average speed from location history."""
        if not locations:
            return 0.0
        
        speeds = [loc.speed for loc in locations if loc.speed is not None]
        if not speeds:
            return 0.0
        
        return sum(speeds) / len(speeds)

    @staticmethod
    def cleanup_old_locations(db: Session, days: int = 30):
        """Delete location history older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        db.query(AgentLocation).filter(
            AgentLocation.created_at < cutoff_date,
            AgentLocation.is_active == 0
        ).delete()
        db.commit()
    @staticmethod
    def get_agents_with_current_locations(db: Session, limit: int = 1000):
        """Get all agents with their current locations and metadata."""
        from app.models.agent import Agent
        from app.models.user import User
        from app.models.delivery import Delivery, DeliveryStatus
        
        agents = db.query(Agent).limit(limit).all()
        agents_data = []
        
        for agent in agents:
            current_location = CRUDLocation.get_current_location(db, agent.id)
            
            # Count active deliveries
            active_deliveries = db.query(Delivery).filter(
                Delivery.agent_id == agent.id,
                Delivery.status.in_([DeliveryStatus.pending, DeliveryStatus.in_progress])
            ).count()
            
            user = db.query(User).filter(User.id == agent.user_id).first()
            
            agents_data.append({
                'agent_id': agent.id,
                'agent_name': user.full_name if user else f"Agent {agent.id}",
                'user_id': agent.user_id,
                'phone': user.phone if user else "N/A",
                'email': user.email if user else "N/A",
                'latitude': current_location.latitude if current_location else agent.current_latitude,
                'longitude': current_location.longitude if current_location else agent.current_longitude,
                'accuracy': current_location.accuracy if current_location else None,
                'speed': current_location.speed if current_location else None,
                'bearing': current_location.bearing if current_location else None,
                'address': current_location.address if current_location else None,
                'status': str(agent.status),
                'assigned_area': agent.assigned_area,
                'current_deliveries_count': active_deliveries,
                'total_earnings': float(agent.total_earnings or 0),
                'last_updated': current_location.timestamp if current_location else agent.updated_at,
                'is_active': current_location.is_active == 1 if current_location else False
            })
        
        return agents_data

    @staticmethod
    def get_customer_active_delivery(db: Session, customer_id: int):
        """Get active delivery for customer with agent location."""
        from app.models.delivery import Delivery, DeliveryStatus
        from app.models.agent import Agent
        from app.models.user import User
        from app.models.customer import Customer
        
        delivery = db.query(Delivery).filter(
            Delivery.customer_id == customer_id,
            Delivery.status.in_([DeliveryStatus.pending, DeliveryStatus.in_progress])
        ).first()
        
        if not delivery:
            return None
        
        agent = db.query(Agent).filter(Agent.id == delivery.agent_id).first()
        agent_location = CRUDLocation.get_current_location(db, agent.id) if agent else None
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        agent_user = db.query(User).filter(User.id == agent.user_id).first() if agent else None
        
        data = {
            'delivery_id': delivery.id,
            'agent_id': agent.id if agent else None,
            'agent_name': agent_user.full_name if agent_user else "Unknown",
            'agent_phone': agent_user.phone if agent_user else "N/A",
            'order_id': delivery.order_id,
            'customer_id': customer_id,
            'customer_name': db.query(User).filter(User.id == customer.user_id).first().full_name if customer else "Unknown",
            'latitude': agent_location.latitude if agent_location else (agent.current_latitude if agent else None),
            'longitude': agent_location.longitude if agent_location else (agent.current_longitude if agent else None),
            'customer_latitude': customer.latitude if customer else None,
            'customer_longitude': customer.longitude if customer else None,
            'status': delivery.status,
            'estimated_arrival': delivery.estimated_delivery_date,
            'actual_delivery_time': delivery.actual_delivery_date,
            'distance_remaining_km': CRUDLocation.calculate_distance(
                agent_location.latitude if agent_location else agent.current_latitude,
                agent_location.longitude if agent_location else agent.current_longitude,
                customer.latitude if customer else 0,
                customer.longitude if customer else 0
            ) if agent and customer else 0,
            'last_updated': agent_location.timestamp if agent_location else delivery.updated_at
        }
        
        return data

    @staticmethod
    def get_map_statistics(db: Session):
        """Get map statistics."""
        from app.models.agent import Agent, AgentStatus
        from app.models.delivery import Delivery, DeliveryStatus
        from datetime import date
        
        # Count agents by status
        total_agents = db.query(Agent).count()
        agents_online = db.query(Agent).filter(Agent.status == AgentStatus.active).count()
        
        # In delivery
        agents_in_delivery = db.query(Delivery).filter(
            Delivery.status == DeliveryStatus.in_progress
        ).distinct(Delivery.agent_id).count()
        
        # Deliveries in progress
        total_deliveries_in_progress = db.query(Delivery).filter(
            Delivery.status == DeliveryStatus.in_progress
        ).count()
        
        # Distance covered today
        today = date.today()
        today_locations = db.query(AgentLocation).filter(
            AgentLocation.created_at >= datetime(today.year, today.month, today.day),
            AgentLocation.is_active == 0  # History only
        ).all()
        
        total_distance = CRUDLocation.calculate_total_distance(today_locations)
        
        # Delivery statistics
        completed_today = db.query(Delivery).filter(
            Delivery.status == DeliveryStatus.delivered,
            Delivery.actual_delivery_date >= datetime(today.year, today.month, today.day)
        ).count()
        
        # Average delivery time
        completed_deliveries = db.query(Delivery).filter(
            Delivery.status == DeliveryStatus.delivered,
            Delivery.actual_delivery_date >= datetime(today.year, today.month, today.day),
            Delivery.delivery_time.isnot(None)
        ).all()
        
        avg_delivery_time = 0.0
        if completed_deliveries:
            total_minutes = sum([
                (d.delivery_time - d.pickup_time).total_seconds() / 60
                for d in completed_deliveries
                if d.pickup_time
            ])
            avg_delivery_time = total_minutes / len(completed_deliveries)
        
        # On-time delivery percentage
        on_time_count = sum(1 for d in completed_deliveries if d.actual_delivery_date <= d.estimated_delivery_date)
        on_time_percentage = (on_time_count / len(completed_deliveries) * 100) if completed_deliveries else 0
        
        return {
            'total_agents': total_agents,
            'agents_online': agents_online,
            'agents_in_delivery': agents_in_delivery,
            'total_deliveries_in_progress': total_deliveries_in_progress,
            'total_distance_covered_today_km': round(total_distance, 2),
            'average_delivery_time_minutes': round(avg_delivery_time, 1),
            'on_time_delivery_percentage': round(on_time_percentage, 1),
            'successful_deliveries_today': completed_today
        }


crud_location = CRUDLocation()