import os
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["AutoML Preprocess"])

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))

class PreprocessRequest(BaseModel):
    filename: str

@router.post("/preprocess", status_code=status.HTTP_200_OK)
def preprocess_dataset(request: PreprocessRequest):
    # Öncelikli olarak uploads/, yoksa data/ klasörüne bak
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(DATA_DIR, request.filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"'{request.filename}' adında bir dosya bulunamadı."
        )

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV okuma hatası: {str(e)}")

    total_rows, total_cols = df.shape
    missing_values = {col: int(val) for col, val in df.isnull().sum().items()}
    column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # Sadece sayısal sütunlar için özet istatistikler ve NaN/Inf temizliği
    numeric_df = df.select_dtypes(include=['number']).replace([np.inf, -np.inf], np.nan)
    
    if not numeric_df.empty:
        # FastAPI JSON'a çevirirken NaN hatası vermesin diye fillna(0) veya None kullanıyoruz
        summary_stats = numeric_df.describe().fillna(0).round(4).to_dict()
    else:
        summary_stats = {}

    return {
        "status": "SUCCESS",
        "filename": request.filename,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "column_types": column_types,
        "missing_values_count": missing_values,
        "summary_statistics": summary_stats
    }