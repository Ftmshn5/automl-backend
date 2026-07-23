from fastapi import APIRouter, HTTPException
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from app.schemas import TrainRequest, TrainResponse, ModelScore

router = APIRouter(prefix="/api/v1", tags=["Training"])

UPLOAD_DIR = "uploads"
MODEL_DIR = "saved_models"

os.makedirs(MODEL_DIR, exist_ok=True)

@router.post("/train", response_model=TrainResponse)
async def train_models(request: TrainRequest):
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"'{request.filename}' dosyası bulunamadı.")

    try:
        if request.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif request.filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise HTTPException(status_code=400, detail="Desteklenmeyen dosya formatı.")

        if request.target_column not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Hedef sütun '{request.target_column}' bulunamadı. Mevcut sütunlar: {list(df.columns[:10])}..."
            )

        # 1. Eksik değerleri temizle/doldur
        df = df.dropna(subset=[request.target_column])
        df = df.fillna(0)

        # 2. X ve y ayrımı
        X = df.drop(columns=[request.target_column])
        y = df[request.target_column]

        # 3. Target (Hedef) metin/kategorik ise sayısal formata çevir (Label Encoding)
        if y.dtype == 'object' or str(y.dtype) == 'category':
            le = LabelEncoder()
            y = le.fit_transform(y.astype(str))

        # 4. Girdi özelliklerini (X) sayısal hale getir
        X = pd.get_dummies(X, drop_first=True)

        # 5. Train-Test Ayrımı
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scores = []
        trained_models = {}

        if request.task_type == "classification":
            models = {
                "Random Forest Classifier": RandomForestClassifier(random_state=42),
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
                "Decision Tree Classifier": DecisionTreeClassifier(random_state=42),
                "Gradient Boosting Classifier": GradientBoostingClassifier(random_state=42)
            }
            
            for name, model in models.items():
                try:
                    model.fit(X_train, y_train)
                    preds = model.predict(X_test)
                    acc = float(accuracy_score(y_test, preds))
                    scores.append(ModelScore(model_name=name, score=acc))
                    trained_models[name] = model
                except Exception as e:
                    print(f"Hata ({name}): {e}")
                    continue

        elif request.task_type == "regression":
            models = {
                "Random Forest Regressor": RandomForestRegressor(random_state=42),
                "Linear Regression": LinearRegression(),
                "Decision Tree Regressor": DecisionTreeRegressor(random_state=42),
                "Gradient Boosting Regressor": GradientBoostingRegressor(random_state=42)
            }
            
            for name, model in models.items():
                try:
                    model.fit(X_train, y_train)
                    preds = model.predict(X_test)
                    r2 = float(r2_score(y_test, preds))
                    scores.append(ModelScore(model_name=name, score=r2))
                    trained_models[name] = model
                except Exception as e:
                    print(f"Hata ({name}): {e}")
                    continue
        else:
            raise HTTPException(status_code=400, detail="Geçersiz görev tipi.")

        if not scores:
            raise HTTPException(status_code=500, detail="Modeller eğitilemedi. Lütfen veri setinizi kontrol edin.")

        # En başarılı modeli seç ve kaydet
        best_model_info = max(scores, key=lambda x: x.score)
        best_model_obj = trained_models[best_model_info.model_name]
        
        saved_model_filename = f"best_model_{request.filename}.joblib"
        saved_model_path = os.path.join(MODEL_DIR, saved_model_filename)
        joblib.dump(best_model_obj, saved_model_path)

        return TrainResponse(
            message=f"AutoML Eğitimi Başarıyla Tamamlandı! En iyi model '{saved_model_filename}' olarak kaydedildi.",
            best_model=best_model_info.model_name,
            best_score=best_model_info.score,
            all_scores=scores
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eğitim hatası: {str(e)}")