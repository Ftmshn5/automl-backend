import os
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

SAVE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "saved_models"))

class PredictRequest(BaseModel):
    job_id: str
    model_name: str
    data: dict

@router.post("/predict")
def predict(request: PredictRequest):
    # Kaydedilmiş model dosyasını bul
    model_filename = f"{request.job_id}_{request.model_name}.joblib"
    model_path = os.path.join(SAVE_DIR, model_filename)

    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Kaydedilmiş model dosyası bulunamadı! Yol: {model_path}"
        )

    try:
        # Modeli diskten yükle
        model = joblib.load(model_path)
        
        # Gelen veriyi DataFrame yapıp One-Hot'a uygula
        input_df = pd.DataFrame([request.data])
        input_df = pd.get_dummies(input_df, drop_first=True)

        # Tahmin üret
        predictions = model.predict(input_df)
        return {
            "status": "SUCCESS",
            "job_id": request.job_id,
            "model_name": request.model_name,
            "prediction": predictions.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin yapılırken hata oluştu: {str(e)}")