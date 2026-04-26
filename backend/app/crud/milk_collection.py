from sqlalchemy.orm import Session
from ..models.milk_collection import MilkCollection
from ..schemas.milk_collection import MilkCollectionCreate

def create_milk_collection(db: Session, collection: MilkCollectionCreate):
    db_collection = MilkCollection(**collection.dict())
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

def get_collections_by_farmer(db: Session, farmer_id: int):
    return db.query(MilkCollection).filter(MilkCollection.farmer_id == farmer_id).all()