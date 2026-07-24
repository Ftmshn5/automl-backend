import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score

def train_single_model(df: pd.DataFrame, target_column: str, model_name: str, task_type: str = "regression") -> dict:
    # Sayısal sütunları seç
    X = df.drop(columns=[target_column]).select_dtypes(include=[np.number])
    y = df[target_column]

    # Eksik değerleri (NaN) sütun ortalaması ile doldur
    X = X.fillna(X.mean())
    y = y.fillna(y.mean() if task_type == "regression" else y.mode()[0])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model Seçimi
    if task_type == "regression":
        models = {
            "RandomForest": RandomForestRegressor(n_estimators=50, random_state=42),
            "GradientBoosting": GradientBoostingRegressor(random_state=42),
            "Ridge": Ridge()
        }
    else: # classification
        models = {
            "RandomForest": RandomForestClassifier(n_estimators=50, random_state=42),
            "GradientBoosting": GradientBoostingClassifier(random_state=42),
            "LogisticRegression": LogisticRegression(max_iter=500)
        }

    model = models.get(model_name)
    if not model:
        raise ValueError(f"Bilinmeyen model tipi: {model_name}")

    # Eğit ve Tahmin Et
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    # Metrik Hesaplama
    if task_type == "regression":
        mse = mean_squared_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        return {"mse": round(float(mse), 4), "r2": round(float(r2), 4)}
    else:
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")
        return {"accuracy": round(float(acc), 4), "f1_score": round(float(f1), 4)}