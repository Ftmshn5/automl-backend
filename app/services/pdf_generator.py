import os
from datetime import datetime
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Türkçe Karakter Desteği için DejaVuSans Font Kaydı
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Linux (Docker) üzerindeki standart DejaVu font yolları
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_bold_path))
    MAIN_FONT = 'DejaVu'
    BOLD_FONT = 'DejaVu-Bold'
else:
    MAIN_FONT = 'Helvetica'
    BOLD_FONT = 'Helvetica-Bold'

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_performance_chart(sub_tasks, task_type, job_id) -> str:
    chart_path = os.path.join(REPORTS_DIR, f"chart_{job_id}.png")
    
    model_names = []
    scores = []
    
    metric_key = "r2" if task_type == "regression" else "f1_score"
    metric_label = "R² Skoru" if task_type == "regression" else "F1 Skoru"

    for t in sub_tasks:
        if t.status == "SUCCESS" and t.metrics:
            model_names.append(t.model_name)
            scores.append(t.metrics.get(metric_key, 0))

    if not model_names:
        return None

    plt.figure(figsize=(6, 3))
    bars = plt.bar(model_names, scores, color=['#1E3A8A', '#3B82F6', '#10B981', '#F59E0B'][:len(model_names)])
    plt.title(f"Model Performans Karşılaştırması ({metric_label})", fontsize=11, fontweight='bold', pad=10)
    plt.ylabel(metric_label, fontsize=9)
    plt.ylim(0, max(scores) * 1.2 if max(scores) > 0 else 1)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.4f}", ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(chart_path, dpi=200)
    plt.close()
    return chart_path

def generate_pdf_report(job, sub_tasks) -> str:
    pdf_filename = f"report_{job.id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], 
        fontName=BOLD_FONT, fontSize=16, 
        textColor=colors.HexColor('#1E3A8A'), spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Heading2'], 
        fontName=BOLD_FONT, fontSize=11, 
        textColor=colors.HexColor('#2563EB'), spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'NormalStyle', parent=styles['Normal'], 
        fontName=MAIN_FONT, fontSize=8.5, leading=12
    )

    story = []

    # 1. Başlık & Künye
    story.append(Paragraph("AutoML Paralel Model Eğitim ve Performans Raporu", title_style))
    story.append(Spacer(1, 5))
    
    meta_data = [
        [Paragraph(f"<b>İş ID (Job ID):</b> {job.id}", normal_style), Paragraph(f"<b>Tarih:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style)],
        [Paragraph(f"<b>Veri Seti:</b> {job.filename}", normal_style), Paragraph(f"<b>Hedef Değişken (Target):</b> {job.target_column}", normal_style)],
        [Paragraph(f"<b>Problem Tipi:</b> {job.task_type.upper()}", normal_style), Paragraph(f"<b>İşlem Durumu:</b> Paralel Tamamlandı", normal_style)]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # 2. Kazanan Model & Özet
    successful_tasks = [t for t in sub_tasks if t.status == "SUCCESS" and t.metrics]
    best_model_name = "Bulunamadı"
    best_score_str = "N/A"
    
    if successful_tasks:
        if job.task_type == "regression":
            best_task = max(successful_tasks, key=lambda x: x.metrics.get("r2", -999))
            best_score_str = f"R² Skoru = {best_task.metrics.get('r2')}"
        else:
            best_task = max(successful_tasks, key=lambda x: x.metrics.get("f1_score", 0))
            best_score_str = f"F1 Skoru = {best_task.metrics.get('f1_score')}"
        best_model_name = best_task.model_name

    story.append(Paragraph("🏆 Eğitim Özeti ve En Başarılı Model", subtitle_style))
    summary_text = (
        f"Veri seti üzerinde <b>{job.total_tasks} farklı algoritma</b> eş zamanlı (paralel) olarak eğitilmiştir. "
        f"Eğitim sonucunda en yüksek performansı gösteren algoritma: <b>{best_model_name}</b> ({best_score_str}).<br/>"
        f"<b>Başarılı Görevler:</b> {job.completed_tasks} | <b>Başarısız/Hatalı:</b> {job.failed_tasks}"
    )
    story.append(Paragraph(summary_text, normal_style))
    story.append(Spacer(1, 12))

    # 3. Model Karşılaştırma Tablosu
    story.append(Paragraph("📊 Detaylı Model Karşılaştırma Tablosu", subtitle_style))
    
    table_data = [[
        Paragraph(f"<b>Model Adı</b>", ParagraphStyle('TH1', parent=normal_style, fontName=BOLD_FONT, textColor=colors.whitesmoke)),
        Paragraph(f"<b>Durum</b>", ParagraphStyle('TH2', parent=normal_style, fontName=BOLD_FONT, textColor=colors.whitesmoke)),
        Paragraph(f"<b>Hesaplanan Metrikler</b>", ParagraphStyle('TH3', parent=normal_style, fontName=BOLD_FONT, textColor=colors.whitesmoke)),
        Paragraph(f"<b>Süre (sn)</b>", ParagraphStyle('TH4', parent=normal_style, fontName=BOLD_FONT, textColor=colors.whitesmoke)),
        Paragraph(f"<b>Yeniden Deneme</b>", ParagraphStyle('TH5', parent=normal_style, fontName=BOLD_FONT, textColor=colors.whitesmoke))
    ]]

    for task in sub_tasks:
        metrics_str = ", ".join([f"{k.upper()}: {v}" for k, v in task.metrics.items()]) if task.metrics else "N/A"
        time_str = f"{task.execution_time:.2f} s" if task.execution_time else "N/A"
        
        table_data.append([
            Paragraph(task.model_name, normal_style),
            Paragraph(task.status, normal_style),
            Paragraph(metrics_str, normal_style),
            Paragraph(time_str, normal_style),
            Paragraph(str(task.retry_count), normal_style)
        ])

    t = Table(table_data, colWidths=[110, 70, 210, 80, 70])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # 4. Performans Grafiği Gömme
    chart_file = generate_performance_chart(sub_tasks, job.task_type, job.id)
    if chart_file and os.path.exists(chart_file):
        story.append(Paragraph("📈 Performans Görselleştirmesi", subtitle_style))
        story.append(Image(chart_file, width=400, height=200))
        story.append(Spacer(1, 10))

    # 5. Otomatik Değerlendirme & Yorum
    story.append(Paragraph("💡 Otomatik Sistem Değerlendirmesi", subtitle_style))
    comment = (
        f"Eğitilen modeller arasında <b>{best_model_name}</b>, veri setinin yapısına ve hedef değişkene en iyi uyumu sağlamıştır. "
        f"Regresyon problemlerinde R² değerinin 1.0'a yaklaşması modelin açıklayıcılık gücünün yüksek olduğunu gösterir. "
        f"Üretilen bu model 'saved_models/' dizinine kaydedilmiş olup, canlı tahminler için kullanıma hazırdır."
    )
    story.append(Paragraph(comment, normal_style))

    doc.build(story)

    if chart_file and os.path.exists(chart_file):
        try:
            os.remove(chart_file)
        except:
            pass

    return pdf_path

import os
from datetime import datetime
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Türkçe Karakter Desteği (DejaVu Font Kaydı)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_bold_path))
    MAIN_FONT = 'DejaVu'
    BOLD_FONT = 'DejaVu-Bold'
else:
    MAIN_FONT = 'Helvetica'
    BOLD_FONT = 'Helvetica-Bold'