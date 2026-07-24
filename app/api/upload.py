import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter(prefix="", tags=["AutoML Upload"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_csv_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Lütfen geçerli bir .csv dosyası yükleyin."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "status": "SUCCESS",
        "message": f"'{file.filename}' dosyası başarıyla yüklendi.",
        "filename": file.filename,
        "saved_path": file_path
    }