import os
import time
import joblib
import pandas as pd
from celery import shared_task
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import TrainingJob, ModelTaskResult
from app.services.model_trainer import train_single_model

SAVE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "saved_models"))
os.makedirs(SAVE_DIR, exist_ok=True)

@shared_task(
    bind=True,
    name="app.tasks.run_single_model_training",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def run_single_model_training(self, task_result_id: str, file_path: str, target_column: str, model_name: str, task_type: str):
    db: Session = SessionLocal()
    start_time = time.time()
    
    task_record = db.query(ModelTaskResult).filter(ModelTaskResult.id == task_result_id).first()
    if task_record:
        task_record.status = "RUNNING"
        task_record.retry_count = self.request.retries
        db.commit()

    try:
        if not os.path.exists(file_path):
            if not os.path.isabs(file_path) and not file_path.startswith("uploads/"):
                file_path = os.path.join("/app/uploads", os.path.basename(file_path))
            elif file_path.startswith("uploads/"):
                file_path = os.path.join("/app", file_path)

        df = pd.read_csv(file_path)

        # Modeli Eğit
        metrics, trained_model = train_single_model(df, target_column, model_name, task_type)
        
        elapsed_time = round(time.time() - start_time, 2)

        # Modeli Diske Kaydet
        if trained_model is not None and task_record:
            job_id_str = str(task_record.job_id)
            model_filename = f"{job_id_str}_{model_name}.joblib"
            model_save_path = os.path.join(SAVE_DIR, model_filename)
            
            joblib.dump(trained_model, model_save_path)
            print(f"✅ MODEL DİSKE KAYDEDİLDİ: {model_save_path}")

        # Başarılı sonucu veritabanına kaydet
        if task_record:
            task_record.status = "SUCCESS"
            task_record.metrics = metrics
            task_record.execution_time = elapsed_time
            db.commit()

            job = db.query(TrainingJob).filter(TrainingJob.id == task_record.job_id).first()
            if job:
                job.completed_tasks += 1
                if job.completed_tasks + job.failed_tasks == job.total_tasks:
                    job.status = "COMPLETED"
                db.commit()

        return {"status": "SUCCESS", "model": model_name, "metrics": metrics, "time": elapsed_time}

    except Exception as exc:
        db.rollback()  # 🟢 VERİTABANI KİLİTLENMESİNİ ENGELLEMEK İÇİN ROLLBACK
        if task_record:
            task_record.error_message = str(exc)
            if self.request.retries >= self.max_retries:
                task_record.status = "FAILURE"
                job = db.query(TrainingJob).filter(TrainingJob.id == task_record.job_id).first()
                if job:
                    job.failed_tasks += 1
                    if job.completed_tasks + job.failed_tasks == job.total_tasks:
                        job.status = "COMPLETED"
                    db.commit()
            else:
                task_record.status = "RETRYING"
            db.commit()

        raise exc
    finally:
        db.close()