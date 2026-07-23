from fastapi import APIRouter, UploadFile, File, HTTPException
import os

router = APIRouter(prefix="/api/v1", tags=["Upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Sadece CSV veya XLSX dosyası yükleyebilirsiniz.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    return {"message": "Dosya başarıyla yüklendi", "filename": file.filename, "path": file_path}