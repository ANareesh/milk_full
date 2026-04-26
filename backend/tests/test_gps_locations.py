"""GPS location tracking tests."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.crud.location import crud_location
from app.models.agent_location import AgentLocation
from app.schemas.location import LocationUpdate


class TestLocationTracking:
    """Test location tracking functionality."""
    
    def test_create_location_record(self, db: Session, agent_id: int):
        """Test creating a location record."""
        location_data = LocationUpdate(
            latitude=28.7041,
            longitude=77.1025,
            accuracy=10.5,
            speed=45.3,
            bearing=180.0,
            address="New Delhi"
        )
        
        location = crud_location.create(db, agent_id, location_data)
        
        assert location.id is not None
        assert location.agent_id == agent_id
        assert location.latitude == 28.7041
        assert location.longitude == 77.1025
        assert location.accuracy == 10.5
        assert location.speed == 45.3
        assert location.is_active == 1
    
    def test_current_location_becomes_history(self, db: Session, agent_id: int):
        """Test that previous location is marked as history."""
        # Create first location
        loc1 = LocationUpdate(
            latitude=28.7041,
            longitude=77.1025,
            accuracy=10.0,
            speed=30.0
        )
        location1 = crud_location.create(db, agent_id, loc1)
        assert location1.is_active == 1
        
        # Create second location
        loc2 = LocationUpdate(
            latitude=28.7042,
            longitude=77.1026,
            accuracy=10.0,
            speed=35.0
        )
        location2 = crud_location.create(db, agent_id, loc2)
        
        # Refresh first location from DB
        db.refresh(location1)
        
        assert location1.is_active == 0
        assert location2.is_active == 1
    
    def test_get_current_location(self, db: Session, agent_id: int):
        """Test retrieving current location."""
        location_data = LocationUpdate(
            latitude=28.7041,
            longitude=77.1025,
            accuracy=5.0,
            speed=40.0
        )
        
        created = crud_location.create(db, agent_id, location_data)
        retrieved = crud_location.get_current_location(db, agent_id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.latitude == 28.7041


class TestDistanceCalculation:
    """Test distance calculation."""
    
    def test_calculate_distance_basic(self):
        """Test distance calculation between two points."""
        # New Delhi to Mumbai (approx 1400 km)
        lat1, lon1 = 28.7041, 77.1025
        lat2, lon2 = 19.0760, 72.8777
        
        distance = crud_location.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Should be approximately 1400 km (±50 km tolerance)
        assert 1350 < distance < 1450
    
    def test_calculate_distance_same_point(self):
        """Test distance calculation for same point."""
        lat, lon = 28.7041, 77.1025
        
        distance = crud_location.calculate_distance(lat, lon, lat, lon)
        
        assert distance == 0.0
    
    def test_calculate_distance_short(self):
        """Test distance calculation for short distance."""
        # 1 km approx
        lat1, lon1 = 28.7041, 77.1025
        lat2, lon2 = 28.7145, 77.1025
        
        distance = crud_location.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Should be approximately 1 km
        assert 0.5 < distance < 1.5
    
    def test_calculate_total_distance(self, db: Session, agent_id: int):
        """Test calculating total distance from route."""
        locations = [
            LocationUpdate(latitude=28.7041, longitude=77.1025),
            LocationUpdate(latitude=28.7145, longitude=77.1025),
            LocationUpdate(latitude=28.7249, longitude=77.1025),
        ]
        
        created_locations = []
        for loc_data in locations:
            loc = crud_location.create(db, agent_id, loc_data)
            created_locations.append(loc)
        
        total_distance = crud_location.calculate_total_distance(created_locations)
        
        # Should be approximately 2 km
        assert 1.5 < total_distance < 2.5
    
    def test_calculate_average_speed(self, db: Session, agent_id: int):
        """Test calculating average speed."""
        locations_data = [
            LocationUpdate(latitude=28.7041, longitude=77.1025, speed=30.0),
            LocationUpdate(latitude=28.7145, longitude=77.1025, speed=40.0),
            LocationUpdate(latitude=28.7249, longitude=77.1025, speed=50.0),
        ]
        
        locations = []
        for loc_data in locations_data:
            loc = crud_location.create(db, agent_id, loc_data)
            locations.append(loc)
        
        avg_speed = crud_location.calculate_average_speed(locations)
        
        # Average of 30, 40, 50 = 40
        assert avg_speed == 40.0


class TestLocationHistory:
    """Test location history."""
    
    def test_get_location_history(self, db: Session, agent_id: int):
        """Test retrieving location history."""
        # Create 5 locations
        for i in range(5):
            location_data = LocationUpdate(
                latitude=28.7041 + i * 0.01,
                longitude=77.1025 + i * 0.01,
                speed=30.0 + i * 5
            )
            crud_location.create(db, agent_id, location_data)
        
        history = crud_location.get_location_history(db, agent_id, hours=24)
        
        assert len(history) == 5
        assert all(loc.agent_id == agent_id for loc in history)
    
    def test_get_location_history_with_time_limit(self, db: Session, agent_id: int):
        """Test retrieving location history with time limit."""
        location_data = LocationUpdate(
            latitude=28.7041,
            longitude=77.1025,
            speed=30.0
        )
        
        # Create current location
        crud_location.create(db, agent_id, location_data)
        
        # Get history for last 1 hour
        history = crud_location.get_location_history(db, agent_id, hours=1)
        
        assert len(history) >= 1


class TestDeliveryRoute:
    """Test delivery route tracking."""
    
    def test_get_delivery_route(self, db: Session, agent_id: int, delivery_id: int):
        """Test retrieving delivery route."""
        # Create locations for delivery
        for i in range(3):
            location_data = LocationUpdate(
                latitude=28.7041 + i * 0.01,
                longitude=77.1025 + i * 0.01,
                speed=40.0
            )
            crud_location.create(db, agent_id, location_data, delivery_id=delivery_id)
        
        route = crud_location.get_delivery_route(db, delivery_id)
        
        assert len(route) == 3
        assert all(loc.delivery_id == delivery_id for loc in route)


class TestLocationValidation:
    """Test location input validation."""
    
    def test_invalid_latitude(self, db: Session, agent_id: int):
        """Test invalid latitude rejection."""
        with pytest.raises(ValueError):
            LocationUpdate(
                latitude=91.0,  # Invalid: > 90
                longitude=77.1025
            )
    
    def test_invalid_longitude(self, db: Session, agent_id: int):
        """Test invalid longitude rejection."""
        with pytest.raises(ValueError):
            LocationUpdate(
                latitude=28.7041,
                longitude=181.0  # Invalid: > 180
            )
    
    def test_invalid_speed(self, db: Session, agent_id: int):
        """Test negative speed rejection."""
        with pytest.raises(ValueError):
            LocationUpdate(
                latitude=28.7041,
                longitude=77.1025,
                speed=-10.0  # Invalid: negative
            )
    
    def test_valid_location_update(self):
        """Test valid location update."""
        location = LocationUpdate(
            latitude=28.7041,
            longitude=77.1025,
            accuracy=5.5,
            speed=35.0,
            bearing=180.0,
            address="Test Location"
        )
        
        assert location.latitude == 28.7041
        assert location.longitude == 77.1025


class TestBatchOperations:
    """Test batch operations."""
    
    def test_cleanup_old_locations(self, db: Session, agent_id: int):
        """Test cleaning up old location records."""
        # Create old location (manually set timestamp)
        old_location = AgentLocation(
            agent_id=agent_id,
            latitude=28.7041,
            longitude=77.1025,
            is_active=0,
            created_at=datetime.utcnow() - timedelta(days=40)
        )
        db.add(old_location)
        db.commit()
        
        # Create recent location
        location_data = LocationUpdate(
            latitude=28.7041,
            longitude=77.1025
        )
        crud_location.create(db, agent_id, location_data)
        
        # Cleanup old records (> 30 days)
        crud_location.cleanup_old_locations(db, days=30)
        
        # Old record should be deleted
        remaining = db.query(AgentLocation).filter(
            AgentLocation.agent_id == agent_id,
            AgentLocation.is_active == 0
        ).count()
        
        assert remaining == 0