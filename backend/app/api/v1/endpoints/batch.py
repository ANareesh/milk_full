from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.dependencies import get_db, get_current_user
from ...models.batch import Batch

router = APIRouter()

@router.post("/")
def create_batch(batch_code: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    batch = Batch(batch_code=batch_code)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return {"msg": "Batch created", "id": batch.id}