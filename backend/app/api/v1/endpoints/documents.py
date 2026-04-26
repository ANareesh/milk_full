from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from ...core.dependencies import get_db, get_current_user
from ...services.documents import save_document

router = APIRouter()

@router.post("/upload")
def upload_document(doc_type: str, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    return save_document(db, user.id, doc_type, file)