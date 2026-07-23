from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

router = APIRouter(prefix="/api/v1", tags=["Reporting"])

MODEL_DIR = "saved_models"
REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)

@router.get("/report/pdf/{model_filename}")
async def generate_pdf_report(model_filename: str):
    """
    Eğitilen model için PDF formatında özet performans raporu üretir ve indirir.
    """
    model_path = os.path.join(MODEL_DIR, model_filename)
    
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model bulunamadı.")

    pdf_filename = f"report_{model_filename.replace('.joblib', '')}.pdf"
    pdf_path = os.path.join(REPORT_DIR, pdf_filename)

    try:
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Başlık
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=20
        )
        story.append(Paragraph("AutoML Model Performans Raporu", title_style))
        story.append(Spacer(1, 12))

        # Model Bilgileri
        body_style = styles['Normal']
        story.append(Paragraph(f"<b>Model Dosyasi:</b> {model_filename}", body_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph("<b>Durum:</b> Egitim ve Tahmin Servisi Aktif", body_style))
        story.append(Spacer(1, 20))

        # Özet Tablo
        table_data = [
            ["Parametre", "Detay"],
            ["Rapor Tipi", "AutoML Model Ozet Raporu"],
            ["Kaydedilen Model", model_filename],
            ["Sistem Durumu", "Aktif / Canliya Hazir"]
        ]

        t = Table(table_data, colWidths=[180, 270])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#EDF2F7")),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
        ]))
        
        story.append(t)
        doc.build(story)

        return FileResponse(
            path=pdf_path, 
            filename=pdf_filename, 
            media_type='application/pdf'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF rapor oluşturulurken hata oluştu: {str(e)}")