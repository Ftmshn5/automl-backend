from fastapi import APIRouter, HTTPException
import pandas as pd
import os
import joblib

from app.schemas import PredictRequest, PredictResponse

router = APIRouter(prefix="/api/v1", tags=["Prediction"])

MODEL_DIR = "saved_models"

@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    model_path = os.path.join(MODEL_DIR, request.model_filename)
    
    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=404, 
            detail=f"'{request.model_filename}' adında eğitilmiş bir model bulunamadı."
        )

    try:
        # 1. Modeli yükle
        model = joblib.load(model_path)

        # 2. Gelen veriyi DataFrame'e dönüştür
        input_df = pd.DataFrame(request.data)

        # 3. Kategorik sütunları One-Hot Encode yap
        input_df = pd.get_dummies(input_df, drop_first=True)

        # 4. Modelin eğitildiği özelliklerle (features) gelen veriyi hizala
        if hasattr(model, "feature_names_in_"):
            feature_names = model.feature_names_in_
            input_df = input_df.reindex(columns=feature_names, fill_value=0)

        # 5. Tahmin üret
        predictions = model.predict(input_df)

        return PredictResponse(
            message="Tahmin başarıyla tamamlandı!",
            predictions=[float(p) for p in predictions]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin sırasında hata oluştu: {str(e)}")