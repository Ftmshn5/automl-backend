import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TrainingJob, ModelTaskResult
from app.services.pdf_generator import generate_pdf_report

router = APIRouter(prefix="", tags=["AutoML Reports"])

@router.get("/reports/{job_id}/pdf", status_code=status.HTTP_200_OK)
def download_pdf_report(job_id: str, db: Session = Depends(get_db)):
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Eğitim işi bulunamadı.")

    if job.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Eğitim henüz tamamlanmadı. Rapor üretilemiyor.")

    sub_tasks = db.query(ModelTaskResult).filter(ModelTaskResult.job_id == job_id).all()

    # PDF Raporunu oluştur
    pdf_path = generate_pdf_report(job, sub_tasks)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF raporu oluşturulamadı.")

    return FileResponse(
        path=pdf_path,
        filename=f"AutoML_Report_{job_id}.pdf",
        media_type="application/pdf"
    )