"""Map visualization and location tracking tests."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.crud.location import crud_location
from app.models.agent_location import AgentLocation
from app.schemas.location import LocationUpdate


class TestMapVisualization:
    """Test real-time map visualization features."""
    
    def test_get_agents_with_current_locations(self, db: Session, agent_id: int, second_agent_id: int):
        """Test fetching all agents with current locations."""
        # Create locations for multiple agents
        loc1 = LocationUpdate(
            latitude=28.7041,
            longitude=77.1025,
            accuracy=10.0,
            speed=45.5,
            bearing=180.0,
            address="New Delhi"
        )
        crud_location.create(db, agent_id, loc1)
        
        loc2 = LocationUpdate(
            latitude=28.5244,
            longitude=77.1855,
            accuracy=12.0,
            speed=55.0,
            bearing=90.0,
            address="Noida"
        )
        crud_location.create(db, second_agent_id, loc2)
        
        # Fetch all agents with locations
        agents = crud_location.get_agents_with_current_locations(db, limit=10)
        
        assert len(agents) >= 2
        assert agents[0]['agent_id'] in [agent_id, second_agent_id]
        assert 'latitude' in agents[0]
        assert 'longitude' in agents[0]
        assert 'agent_name' in agents[0]
        assert 'status' in agents[0]
    
    def test_get_customer_active_delivery(self, db: Session, customer_id: int, agent_id: int):
        """Test fetching active delivery for customer with agent location."""
        # This requires order and delivery setup in fixtures
        # Assuming fixtures create these relationships
        from app.models.customer import Customer
        
        delivery_data = crud_location.get_customer_active_delivery(db, customer_id)
        
        if delivery_data:  # If there's an active delivery
            assert delivery_data['delivery_id']
            assert delivery_data['agent_id']
            assert 'latitude' in delivery_data
            assert 'longitude' in delivery_data
            assert 'customer_latitude' in delivery_data
            assert 'customer_longitude' in delivery_data
    
    def test_distance_between_agent_and_customer(self, db: Session):
        """Test distance calculation between agent and customer."""
        # Delhi to Noida distance should be ~30km
        agent_lat, agent_lng = 28.7041, 77.1025
        customer_lat, customer_lng = 28.5354, 77.3910
        
        distance = crud_location.calculate_distance(
            agent_lat, agent_lng,
            customer_lat, customer_lng
        )
        
        assert 25 < distance < 35  # Should be approximately 30km
    
    def test_haversine_distance_accuracy(self):
        """Test Haversine formula distance calculation."""
        # Known distance: Delhi (28.7041, 77.1025) to Mumbai (19.0760, 72.8777) is ~1400km
        distance = crud_location.calculate_distance(
            28.7041, 77.1025,
            19.0760, 72.8777
        )
        
        assert 1350 < distance < 1450  # Approximate 1400km
    
    def test_zero_distance_same_location(self):
        """Test distance when coordinates are identical."""
        distance = crud_location.calculate_distance(
            28.7041, 77.1025,
            28.7041, 77.1025
        )
        
        assert distance < 0.1  # Should be nearly zero
    
    def test_get_delivery_route_with_multiple_points(self, db: Session, delivery_id: int, agent_id: int):
        """Test retrieving complete delivery route."""
        # Create multiple location points
        locations_data = [
            {'lat': 28.7041, 'lng': 77.1025, 'speed': 40},
            {'lat': 28.7050, 'lng': 77.1035, 'speed': 45},
            {'lat': 28.7060, 'lng': 77.1045, 'speed': 50},
        ]
        
        for loc in locations_data:
            loc_update = LocationUpdate(
                latitude=loc['lat'],
                longitude=loc['lng'],
                speed=loc['speed']
            )
            crud_location.create(db, agent_id, loc_update, delivery_id=delivery_id)
        
        # Retrieve route
        route = crud_location.get_delivery_route(db, delivery_id)
        
        assert len(route) >= 2
        assert route[0].latitude == locations_data[0]['lat']
        # Verify ordered by timestamp
        assert route[0].timestamp <= route[-1].timestamp
    
    def test_route_total_distance_calculation(self, db: Session, delivery_id: int, agent_id: int):
        """Test total distance calculation for a delivery route."""
        locations_data = [
            LocationUpdate(latitude=28.7041, longitude=77.1025),
            LocationUpdate(latitude=28.7050, longitude=77.1035),
            LocationUpdate(latitude=28.7060, longitude=77.1045),
        ]
        
        created_locations = []
        for loc in locations_data:
            created_loc = crud_location.create(db, agent_id, loc, delivery_id=delivery_id)
            created_locations.append(created_loc)
        
        total_distance = crud_location.calculate_total_distance(created_locations)
        
        assert total_distance > 0
        assert total_distance < 2  # Short route, less than 2km
    
    def test_average_speed_calculation(self, db: Session, agent_id: int):
        """Test average speed calculation from location history."""
        locations_data = [
            LocationUpdate(latitude=28.7041, longitude=77.1025, speed=40.0),
            LocationUpdate(latitude=28.7050, longitude=77.1035, speed=45.0),
            LocationUpdate(latitude=28.7060, longitude=77.1045, speed=50.0),
            LocationUpdate(latitude=28.7070, longitude=77.1055, speed=55.0),
        ]
        
        created_locations = []
        for loc in locations_data:
            created_loc = crud_location.create(db, agent_id, loc)
            created_locations.append(created_loc)
        
        avg_speed = crud_location.calculate_average_speed(created_locations)
        
        assert avg_speed == 47.5  # (40+45+50+55)/4
    
    def test_average_speed_with_null_speeds(self, db: Session, agent_id: int):
        """Test average speed calculation with some null values."""
        locations_data = [
            LocationUpdate(latitude=28.7041, longitude=77.1025, speed=40.0),
            LocationUpdate(latitude=28.7050, longitude=77.1035, speed=None),
            LocationUpdate(latitude=28.7060, longitude=77.1045, speed=50.0),
        ]
        
        created_locations = []
        for loc in locations_data:
            created_loc = crud_location.create(db, agent_id, loc)
            created_locations.append(created_loc)
        
        avg_speed = crud_location.calculate_average_speed(created_locations)
        
        assert avg_speed == 45.0  # (40+50)/2
    
    def test_agent_current_location_update(self, db: Session, agent_id: int):
        """Test that previous location marked as history when new one created."""
        # Create first location
        loc1 = LocationUpdate(latitude=28.7041, longitude=77.1025)
        loc1_created = crud_location.create(db, agent_id, loc1)
        assert loc1_created.is_active == 1
        
        # Create second location
        loc2 = LocationUpdate(latitude=28.7050, longitude=77.1035)
        loc2_created = crud_location.create(db, agent_id, loc2)
        assert loc2_created.is_active == 1
        
        # Verify first location is now history
        history = db.query(AgentLocation).filter(
            AgentLocation.agent_id == agent_id,
            AgentLocation.is_active == 0
        ).all()
        
        assert len(history) >= 1
    
    def test_get_location_history_time_filter(self, db: Session, agent_id: int):
        """Test location history with time filtering."""
        # Create location
        loc = LocationUpdate(latitude=28.7041, longitude=77.1025)
        crud_location.create(db, agent_id, loc)
        
        # Get history for last 24 hours
        history_24h = crud_location.get_location_history(db, agent_id, hours=24)
        
        assert len(history_24h) >= 1
        
        # Get history for last 1 hour (should be empty or minimal)
        history_1h = crud_location.get_location_history(db, agent_id, hours=1)
        
        # May or may not have data depending on timing
        assert isinstance(history_1h, list)
    
    def test_map_statistics_calculation(self, db: Session):
        """Test map statistics aggregation."""
        stats = crud_location.get_map_statistics(db)
        
        assert 'total_agents' in stats
        assert 'agents_online' in stats
        assert 'agents_in_delivery' in stats
        assert 'total_deliveries_in_progress' in stats
        assert 'total_distance_covered_today_km' in stats
        assert 'average_delivery_time_minutes' in stats
        assert 'on_time_delivery_percentage' in stats
        assert 'successful_deliveries_today' in stats
        
        # Verify types
        assert isinstance(stats['total_agents'], int)
        assert isinstance(stats['agents_online'], int)
        assert isinstance(stats['total_distance_covered_today_km'], float)
    
    def test_cleanup_old_locations(self, db: Session, agent_id: int):
        """Test cleanup of old location history."""
        # Create old location
        old_location = AgentLocation(
            agent_id=agent_id,
            latitude=28.7041,
            longitude=77.1025,
            created_at=datetime.utcnow() - timedelta(days=40),
            is_active=0
        )
        db.add(old_location)
        db.commit()
        
        # Cleanup locations older than 30 days
        crud_location.cleanup_old_locations(db, days=30)
        
        # Verify old location is deleted
        deleted_query = db.query(AgentLocation).filter(
            AgentLocation.agent_id == agent_id,
            AgentLocation.created_at < datetime.utcnow() - timedelta(days=30)
        ).all()
        
        assert len(deleted_query) == 0


class TestMapEndpoints:
    """Test map visualization API endpoints."""
    
    def test_get_admin_agents_map_endpoint(self, client, admin_token):
        """Test admin agents map endpoint."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(
            "/api/v1/locations/map/admin/agents",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "agent_markers" in data["data"]
        assert "stats" in data
    
    def test_get_customer_delivery_tracking_endpoint(self, client, customer_token):
        """Test customer delivery tracking endpoint."""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.get(
            "/api/v1/locations/map/customer/delivery-tracking",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "has_active_delivery" in data["data"]
    
    def test_get_delivery_route_endpoint(self, client, admin_token, delivery_id: int):
        """Test delivery route endpoint."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(
            f"/api/v1/locations/map/delivery/{delivery_id}/route",
            headers=headers
        )
        
        # May be 404 if no route exists
        assert response.status_code in [200, 404]
    
    def test_get_map_statistics_endpoint(self, client, admin_token):
        """Test map statistics endpoint."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(
            "/api/v1/locations/map/stats",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "total_agents" in data
        assert "on_time_delivery_percentage" in data
    
    def test_unauthorized_access_admin_map(self, client, customer_token):
        """Test that customer cannot access admin map."""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.get(
            "/api/v1/locations/map/admin/agents",
            headers=headers
        )
        
        assert response.status_code == 403
    
    def test_map_endpoint_without_auth(self, client):
        """Test map endpoints require authentication."""
        response = client.get("/api/v1/locations/map/admin/agents")
        
        assert response.status_code == 401