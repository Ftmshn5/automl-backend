import os
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter(prefix="", tags=["AutoML Predict"])

SAVED_MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "saved_models"))

class PredictRequest(BaseModel):
    model_filename: str
    features: List[Dict[str, Any]]  # Örn: [{"feature_1": 12.5, "feature_2": 3.4}]

@router.post("/predict", status_code=status.HTTP_200_OK)
def make_prediction(request: PredictRequest):
    model_path = os.path.join(SAVED_MODELS_DIR, request.model_filename)

    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"'{request.model_filename}' adında kaydedilmiş bir model bulunamadı."
        )

    try:
        model = joblib.load(model_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model yüklenirken hata oluştu: {str(e)}")

    try:
        input_df = pd.DataFrame(request.features)
        predictions = model.predict(input_df)
        
        return {
            "status": "SUCCESS",
            "model_used": request.model_filename,
            "predictions": [round(float(p), 4) for p in predictions]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tahmin üretilirken hata oluştu: {str(e)}")