from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.dependencies import get_db, get_current_user
from ...models.feedback import Feedback

router = APIRouter()

@router.post("/")
def submit_feedback(message: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    fb = Feedback(user_id=user.id, message=message)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"msg": "Feedback submitted", "id": fb.id}