from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.api.upload import router as upload_router
from app.api.analyze import router as analyze_router
from app.api.preprocess import router as preprocess_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=getattr(settings, "PROJECT_NAME", "AutoML API"),
    version="1.0.0",
    description="Asenkron Paralel AutoML Eğitim ve Raporlama API"
)

# Router'lar
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(preprocess_router)

@app.get("/")
def read_root():
    return {"message": "AutoML Backend API Başarıyla Çalışıyor!"}