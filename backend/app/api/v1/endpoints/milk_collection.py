from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...schemas.milk_collection import MilkCollectionCreate, MilkCollectionResponse
from ...crud import milk_collection as crud
from ...core.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=MilkCollectionResponse)
def collect_milk(
    collection: MilkCollectionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Optionally, check user role (e.g., only agents can collect)
    return crud.create_milk_collection(db, collection)

@router.get("/farmer/{farmer_id}", response_model=list[MilkCollectionResponse])
def get_farmer_collections(
    farmer_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.get_collections_by_farmer(db, farmer_id)