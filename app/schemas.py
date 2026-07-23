from pydantic import BaseModel
from typing import List, Optional

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

    # --- Veri Ön İşleme Şemaları ---
class PreprocessRequest(BaseModel):
    filename: str
    impute_strategy: Optional[str] = "mean"  # "mean", "median", "drop"
    encode_categorical: Optional[bool] = True

class PreprocessResponse(BaseModel):
    message: str
    processed_filename: str
    rows_after: int
    columns_after: int