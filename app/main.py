from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

from app.api.upload import router as upload_router
from app.api.preprocess import router as preprocess_router
from app.api.train import router as train_router
from app.api.predict import router as predict_router
from app.api.report import router as report_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AutoML Paralel Rapor Servisi")

# React Frontend bağlantısı için CORS İzni
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme aşamasında tüm originlere izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(preprocess_router)
app.include_router(train_router)
app.include_router(predict_router)
app.include_router(report_router)