from fastapi import APIRouter, HTTPException
import pandas as pd
import os
from app.schemas import PreprocessRequest, PreprocessResponse

router = APIRouter(prefix="/api/v1", tags=["Preprocessing"])

UPLOAD_DIR = "uploads"

@router.post("/preprocess", response_model=PreprocessResponse)
async def preprocess_dataset(request: PreprocessRequest):
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dosya bulunamadı.")
        
    try:
        # Dosyayı oku
        if request.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif request.filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise HTTPException(status_code=400, detail="Desteklenmeyen dosya formatı.")
            
        # 1. Eksik Veri İşleme (Imputation / Drop)
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if request.impute_strategy == "mean":
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        elif request.impute_strategy == "median":
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        elif request.impute_strategy == "drop":
            df = df.dropna()

        # Kalan eksik kategorik verileri mod (en çok tekrar eden) ile doldur
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")

        # 2. Kategorik Verileri Dönüştürme (One-Hot Encoding)
        if request.encode_categorical and len(categorical_cols) > 0:
            df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

        # İşlenmiş dosyayı kaydet
        processed_filename = f"processed_{request.filename}"
        processed_path = os.path.join(UPLOAD_DIR, processed_filename)
        
        if request.filename.endswith('.csv'):
            df.to_csv(processed_path, index=False)
        else:
            df.to_excel(processed_path, index=False)

        return PreprocessResponse(
            message="Veri önişleme başarıyla tamamlandı.",
            processed_filename=processed_filename,
            rows_after=len(df),
            columns_after=len(df.columns)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Önişleme hatası: {str(e)}")