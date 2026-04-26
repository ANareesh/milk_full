"""Base CRUD class."""
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional, List, Any

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD class."""

    def __init__(self, model: Type[ModelType]):
        """Initialize CRUD base."""
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get item by id."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple items."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create new item."""
        obj_data = obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update item."""
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> Optional[ModelType]:
        """Delete item."""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def count(self, db: Session) -> int:
        """Count total items."""
        return db.query(self.model).count()
