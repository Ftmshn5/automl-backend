import math
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score

def clean_metric_val(val):
    """PostgreSQL JSON alanının çökmesini engellemek için NaN/Inf değerlerini None (null) yapar."""
    if val is None or math.isnan(val) or math.isinf(val):
        return None
    return round(float(val), 4)

def train_single_model(df: pd.DataFrame, target_column: str, model_name: str, task_type: str = "regression"):
    if target_column not in df.columns:
        raise ValueError(f"Hedef değişken '{target_column}' veri setinde bulunamadı!")

    # Target verisini sayısal formata dönüştür (Regresyon ise)
    if task_type == "regression":
        try:
            df[target_column] = pd.to_numeric(df[target_column])
        except Exception:
            raise ValueError(f"Hedef değişken '{target_column}' regresyon için sayısal tipe dönüştürülemedi!")

    # Target ve Features ayırma
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Metin / Kategorik sütunları sayısal hale getir (One-Hot Encoding)
    X = pd.get_dummies(X, drop_first=True)
    X = X.select_dtypes(include=[np.number])

    if X.empty:
        raise ValueError("Eğitim için kullanılabilir sayısal bir öznitelik (feature) bulunamadı!")

    # Eksik değerleri doldur
    X = X.fillna(X.mean())
    y = y.fillna(y.mean() if task_type == "regression" else y.mode()[0])

    # Küçük veri setlerinde train_test_split patlamasın diye kontrol
    test_size = 0.2 if len(df) >= 10 else 0.4
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

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

    # 🟢 CIFT KONTROL: 'if not model' yapmadan direkt key var mı kontrol ediyoruz (len() tetiklenmesin)
    if model_name not in models:
        raise ValueError(f"Bilinmeyen model tipi: {model_name}")

    model = models[model_name]

    # Modeli Eğit
    model.fit(X_train, y_train)

    # Tahmin Yap
    preds = model.predict(X_test)

    # Metrik Hesaplama (NaN temizliği yapılıyor)
    if task_type == "regression":
        mse = mean_squared_error(y_test, preds)
        r2 = r2_score(y_test, preds) if len(y_test) > 1 else None
        metrics = {
            "mse": clean_metric_val(mse),
            "r2": clean_metric_val(r2)
        }
    else:
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")
        metrics = {
            "accuracy": clean_metric_val(acc),
            "f1_score": clean_metric_val(f1)
        }

    return metrics, model