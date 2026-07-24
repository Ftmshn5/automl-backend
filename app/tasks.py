import os
import time
import pandas as pd
from celery import shared_task
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import TrainingJob, ModelTaskResult
from app.services.model_trainer import train_single_model  # Tekli model eğitici

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

@shared_task(
    bind=True,
    name="app.tasks.run_single_model_training",
    autoretry_for=(Exception,),       # Herhangi bir hatada tekrar dene
    retry_kwargs={'max_retries': 3},  # En fazla 3 kez dene
    retry_backoff=True                # Exponential backoff (bekleme süresini katlayarak artır)
)
def run_single_model_training(self, task_result_id: str, filename: str, target_column: str, model_name: str, task_type: str):
    db: Session = SessionLocal()
    start_time = time.time()
    
    # Veritabanından ilgili alt görevi çek ve durumunu RUNNING yap
    task_record = db.query(ModelTaskResult).filter(ModelTaskResult.id == task_result_id).first()
    if task_record:
        task_record.status = "RUNNING"
        task_record.retry_count = self.request.retries
        db.commit()

    try:
        file_path = os.path.join(DATA_DIR, filename)
        df = pd.read_csv(file_path)

        # Seçilen modeli eğit
        metrics = train_single_model(df, target_column, model_name, task_type)
        
        elapsed_time = round(time.time() - start_time, 2)

        # Başarılı sonucu veritabanına kaydet
        if task_record:
            task_record.status = "SUCCESS"
            task_record.metrics = metrics
            task_record.execution_time = elapsed_time
            db.commit()

            # Ana Job'ın ilerleme durumunu güncelle
            job = db.query(TrainingJob).filter(TrainingJob.id == task_record.job_id).first()
            if job:
                job.completed_tasks += 1
                if job.completed_tasks + job.failed_tasks == job.total_tasks:
                    job.status = "COMPLETED"
                db.commit()

        return {"status": "SUCCESS", "model": model_name, "metrics": metrics, "time": elapsed_time}

    except Exception as exc:
        # Hata durumunda veritabanını güncelle
        if task_record:
            task_record.error_message = str(exc)
            if self.request.retries >= self.max_retries:
                task_record.status = "FAILURE"
                job = db.query(TrainingJob).filter(TrainingJob.id == task_record.job_id).first()
                if job:
                    job.failed_tasks += 1
                    if job.completed_tasks + job.failed_tasks == job.total_tasks:
                        job.status = "COMPLETED" # Kısmi başarıyla tamamlama
                    db.commit()
            else:
                task_record.status = "RETRYING"
            db.commit()

        db.close()
        raise exc  # Celery'nin retry yapabilmesi için hatayı fırlatıyoruz
    finally:
        db.close()