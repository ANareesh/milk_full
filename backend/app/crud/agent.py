"""Agent CRUD operations."""
from sqlalchemy.orm import Session
from typing import Optional, List

from app.crud.base import CRUDBase
from app.models.agent import Agent, AgentStatus
from app.schemas.agent import AgentCreate, AgentUpdate


class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    """CRUD operations for Agent model."""

    def get_by_user_id(self, db: Session, user_id: int) -> Optional[Agent]:
        """Get agent by user id."""
        return db.query(Agent).filter(Agent.user_id == user_id).first()

    def get_by_agent_code(self, db: Session, agent_code: str) -> Optional[Agent]:
        """Get agent by agent code."""
        return db.query(Agent).filter(Agent.agent_code == agent_code).first()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get agents by status."""
        return db.query(Agent).filter(Agent.status == status).offset(skip).limit(limit).all()

    def get_available_agents(self, db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get available agents for delivery."""
        return db.query(Agent).filter(
            Agent.available_for_delivery == True,
            Agent.status == AgentStatus.active
        ).offset(skip).limit(limit).all()

    def get_by_assigned_area(self, db: Session, area: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get agents by assigned area."""
        return db.query(Agent).filter(Agent.assigned_area == area).offset(skip).limit(limit).all()

    def update_location(self, db: Session, agent: Agent, latitude: float, longitude: float) -> Agent:
        """Update agent location."""
        agent.current_latitude = latitude
        agent.current_longitude = longitude
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    def update_earnings(self, db: Session, agent: Agent, amount: float) -> Agent:
        """Update agent earnings."""
        agent.total_earnings += amount
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    def increment_deliveries(self, db: Session, agent: Agent) -> Agent:
        """Increment total deliveries."""
        agent.total_deliveries += 1
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    def update_status(self, db: Session, agent: Agent, status: str) -> Agent:
        """Update agent status."""
        agent.status = status
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent


crud_agent = CRUDAgent(Agent)
