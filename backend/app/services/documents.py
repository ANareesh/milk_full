import shutil
from ..models.document import Document

def save_document(db, user_id, doc_type, file):
    file_location = f"uploads/{user_id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    doc = Document(user_id=user_id, doc_type=doc_type, file_path=file_location)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"msg": "Uploaded", "file_path": file_location}