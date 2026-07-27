FROM python:3.10-slim

# Çalışma dizini
WORKDIR /app

# 🇹🇷 TÜRKÇE FONT VE SİSTEM PAKETLERİ
# ReportLab ve Matplotlib'in Türkçe karakterleri (ş, ğ, ı, Ç, ö, ü) ve çizimleri sorunsuz işlemesi için
RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    fonts-dejavu-core \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Varsayılan başlatma komutu (FastAPI / Uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]