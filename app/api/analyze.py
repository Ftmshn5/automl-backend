from fastapi import APIRouter, HTTPException
import pandas as pd
import os
from app.schemas import DatasetAnalysisResponse, ColumnSummary

router = APIRouter(prefix="/api/v1", tags=["Analysis"])

UPLOAD_DIR = "uploads"

@router.post("/analyze/{filename}", response_model=DatasetAnalysisResponse)
async def analyze_dataset(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dosya bulunamadı.")
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise HTTPException(status_code=400, detail="Desteklenmeyen dosya formatı.")
            
        columns_summary = []
        for col in df.columns:
            columns_summary.append(
                ColumnSummary(
                    name=str(col),
                    data_type=str(df[col].dtype),
                    missing_values=int(df[col].isnull().sum()),
                    unique_values=int(df[col].nunique())
                )
            )
            
        return DatasetAnalysisResponse(
            filename=filename,
            total_rows=len(df),
            total_columns=len(df.columns),
            columns=columns_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Veri analizi sırasında hata oluştu: {str(e)}")