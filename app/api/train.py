import os
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TrainingJob, ModelTaskResult
from app.celery_app import celery_app

router = APIRouter(prefix="", tags=["AutoML Model Training"])

class TrainRequest(BaseModel):
    filename: str = Field(default="THYZ_2025_Oturum_1_Translation.csv")
    target_column: str = Field(default="translation_z")
    task_type: str = Field(default="regression")

@router.post("/train-async", status_code=status.HTTP_202_ACCEPTED)
def train_model_async_endpoint(request: TrainRequest, db: Session = Depends(get_db)):
    models_to_train = ["RandomForest", "GradientBoosting", "Ridge"] if request.task_type == "regression" else ["RandomForest", "GradientBoosting", "LogisticRegression"]

    # 1. Veritabanında Ana İş (TrainingJob) Oluştur
    job = TrainingJob(
        filename=request.filename,
        target_column=request.target_column,
        task_type=request.task_type,
        status="RUNNING",
        total_tasks=len(models_to_train)
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 2. Her Model İçin Alt Görev (Sub-task) Tanımla ve Celery Kuyruğuna At
    sub_task_ids = []
    for model_name in models_to_train:
        task_record = ModelTaskResult(
            job_id=job.id,
            model_name=model_name,
            status="PENDING"
        )
        db.add(task_record)
        db.commit()
        db.refresh(task_record)

        # Celery görevini tetikle
        celery_app.send_task(
            "app.tasks.run_single_model_training",
            args=[task_record.id, request.filename, request.target_column, model_name, request.task_type]
        )
        sub_task_ids.append(task_record.id)

    return {
        "status": "queued",
        "message": f"{len(models_to_train)} farklı model eğitimi paralel olarak başlatıldı.",
        "job_id": job.id,
        "sub_tasks": sub_task_ids
    }

@router.get("/jobs/{job_id}", status_code=status.HTTP_200_OK)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Eğitim işi bulunamadı.")

    sub_tasks = db.query(ModelTaskResult).filter(ModelTaskResult.job_id == job_id).all()

    return {
        "job_id": job.id,
        "filename": job.filename,
        "overall_status": job.status,
        "progress": f"{job.completed_tasks + job.failed_tasks}/{job.total_tasks}",
        "models": [
            {
                "model_name": t.model_name,
                "status": t.status,
                "metrics": t.metrics,
                "execution_time": t.execution_time,
                "retries": t.retry_count,
                "error": t.error_message
            }
            for t in sub_tasks
        ]
    }