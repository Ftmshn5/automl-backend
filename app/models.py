import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    target_column = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Alt görevlerle ilişki
    sub_tasks = relationship("ModelTaskResult", back_populates="job", cascade="all, delete-orphan")


class ModelTaskResult(Base):
    __tablename__ = "model_task_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("training_jobs.id"), nullable=False)
    model_name = Column(String, nullable=False)  # Random Forest, XGBoost vb.
    status = Column(String, default="PENDING")   # PENDING, RUNNING, SUCCESS, FAILURE, RETRYING
    metrics = Column(JSON, nullable=True)        # {"r2": 0.85, "mse": 0.12}
    execution_time = Column(Float, nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("TrainingJob", back_populates="sub_tasks")