from pydantic import BaseModel
from typing import List, Optional

# --- 1. Veri Analizi Şemaları ---
class ColumnSummary(BaseModel):
    name: str
    data_type: str
    missing_values: int
    unique_values: int

class DatasetAnalysisResponse(BaseModel):
    filename: str
    total_rows: int
    total_columns: int
    columns: List[ColumnSummary]


# --- 2. Veri Ön İşleme Şemaları ---
class PreprocessRequest(BaseModel):
    filename: str
    impute_strategy: Optional[str] = "mean"  # "mean", "median", "drop"
    encode_categorical: Optional[bool] = True

class PreprocessResponse(BaseModel):
    message: str
    processed_filename: str
    rows_after: int
    columns_after: int


# --- 3. Model Eğitim Şemaları ---
class TrainRequest(BaseModel):
    filename: str
    target_column: str
    task_type: Optional[str] = "classification"  # "classification" veya "regression"

class ModelScore(BaseModel):
    model_name: str
    score: float

class TrainResponse(BaseModel):
    message: str
    best_model: str
    best_score: float
    all_scores: List[ModelScore]

    # --- Tahmin (Prediction) Şemaları ---
class PredictRequest(BaseModel):
    model_filename: str  # Kaydedilen modelin adı (ör: best_model_THYZ_2025_Oturum_1_Translation.csv.joblib)
    data: List[dict]     # Tahmin yapılacak veri satırları (JSON listesi)

class PredictResponse(BaseModel):
    message: str
    predictions: List[float]

    # --- Raporlama (Report) Şemaları ---
class ReportResponse(BaseModel):
    filename: str
    best_model: str
    best_score: float
    total_models_evaluated: int
    all_scores: List[ModelScore]