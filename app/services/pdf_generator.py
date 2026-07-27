import os
import io
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(job, tasks, output_filename="report.pdf"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Özel Stiller
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=0,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    # 1. BAŞLIK BÖLÜMÜ
    story.append(Paragraph("AutoML Paralel Model Eğitim ve Performans Raporu", title_style))
    
    meta_text = f"""
    <b>İş Kimliği (Job ID):</b> {job.id}<br/>
    <b>Veri Seti Dosyası:</b> {job.filename}<br/>
    <b>Hedef Değişken (Target):</b> {job.target_column}
    """
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(Spacer(1, 5))

    # 2. İSTATİSTİK ÖZET KARTLARI (SUMMARY CARDS)
    completed_tasks = [t for t in tasks if t.status == 'SUCCESS']
    best_model = None
    best_r2 = -float('inf')
    
    for t in completed_tasks:
        if t.metrics and 'r2' in t.metrics:
            if t.metrics['r2'] > best_r2:
                best_r2 = t.metrics['r2']
                best_model = t.model_name

    card_data = [
        [
            Paragraph(f"<b>Toplam Model:</b><br/>{len(tasks)}", body_style),
            Paragraph(f"<b>Başarılı:</b><br/>{len(completed_tasks)}", body_style),
            Paragraph(f"<b>En İyi Model:</b><br/>{best_model or 'N/A'}", body_style),
            Paragraph(f"<b>En Yüksek R²:</b><br/>{f'{best_r2:.4f}' if best_model else 'N/A'}", body_style)
        ]
    ]
    card_table = Table(card_data, colWidths=[130, 130, 140, 140])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(card_table)
    story.append(Spacer(1, 15))

    # 3. YAN YANA GRAFİKLER (MODEL KIYASLAMA + FEATURE IMPORTANCE)
    model_names = [t.model_name for t in completed_tasks]
    r2_scores = [t.metrics.get('r2', 0) if t.metrics else 0 for t in completed_tasks]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5), dpi=200)
    
    # Grafik 1: Model Kıyaslama
    if model_names:
        bars = ax1.bar(model_names, r2_scores, color='#2563EB', width=0.5)
        ax1.set_title("Model Performans Kıyaslaması (R²)", fontsize=10, fontweight='bold', pad=10)
        ax1.set_ylabel("Skor", fontsize=8)
        ax1.grid(axis='y', linestyle='--', alpha=0.5)
        ax1.tick_params(axis='both', labelsize=8)
        for bar in bars:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', ha='center', va='bottom' if yval>=0 else 'top', fontsize=7)
    else:
        ax1.text(0.5, 0.5, "Veri Yok", ha='center', va='center')

    # Grafik 2: Öznitelik Önemi (Feature Importance)
    try:
        model_path = f"/app/saved_models/{job.id}_{best_model}.joblib" if best_model else None
        if model_path and os.path.exists(model_path):
            model_obj = joblib.load(model_path)
            if hasattr(model_obj, 'feature_importances_'):
                importances = model_obj.feature_importances_
                feats = [f"Feature {i+1}" for i in range(len(importances))]
                top_idx = np.argsort(importances)[-5:]
                ax2.barh([feats[i] for i in top_idx], importances[top_idx], color='#059669', height=0.5)
                ax2.set_title(f"En Önemli Değişkenler ({best_model})", fontsize=10, fontweight='bold', pad=10)
                ax2.tick_params(axis='both', labelsize=8)
            else:
                ax2.text(0.5, 0.5, "Öznitelik Önemi Desteklenmiyor", ha='center', va='center', fontsize=8)
        else:
            ax2.text(0.5, 0.5, "Model Dosyası Bulunamadı", ha='center', va='center', fontsize=8)
    except Exception:
        ax2.text(0.5, 0.5, "Grafik Üretilemedi", ha='center', va='center', fontsize=8)

    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight')
    plt.close()
    img_buf.seek(0)
    
    story.append(Image(img_buf, width=7.2*inch, height=2.5*inch))
    story.append(Spacer(1, 15))

    # 4. ŞIK TABLO (TABULAR DATA)
    story.append(Paragraph("Model Detaylı Sonuçları", section_heading))
    
    table_data = [["Model Adı", "Durum", "Hesaplanan Metrikler", "Süre (sn)", "Tekrar"]]
    for t in tasks:
        metrics_str = f"MSE: {t.metrics.get('mse', 0):.2f}, R2: {t.metrics.get('r2', 0):.4f}" if t.metrics else "N/A"
        table_data.append([
            t.model_name,
            t.status,
            metrics_str,
            f"{t.execution_time:.2f} s" if t.execution_time else "-",
            str(t.retries)
        ])

    table = Table(table_data, colWidths=[110, 70, 220, 80, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))

    # 5. CANLI TAHMİN KUTUSU & DEĞERLENDİRME
    story.append(Paragraph("Otomatik Sistem Değerlendirmesi ve Tahmin Servisi", section_heading))
    eval_text = f"""
    Eğitilen <b>{len(tasks)}</b> adet model arasından en yüksek başarı oranını (R²: <b>{best_r2:.4f}</b>) gösteren 
    <b>{best_model}</b> modeli seçilmiştir.<br/><br/>
    <b>Canlı Tahmin Durumu:</b> Seçilen model <code>saved_models/{job.id}_{best_model}.joblib</code> yoluna başarıyla 
    serileştirilmiştir. API üzerinden <code>/predict</code> uç noktası kullanılarak anlık tahminler üretilebilir.
    """
    
    eval_table = Table([[Paragraph(eval_text, body_style)]], colWidths=[540])
    eval_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BFDBFE')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(eval_table)

    # Dokümanı Derle
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()