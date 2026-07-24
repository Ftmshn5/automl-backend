# 🚀 Asenkron Paralel AutoML Eğitim ve Raporlama Servisi

Bu proje; kullanıcının yüklediği CSV veri setleri üzerinde birden fazla makine öğrenmesi algoritmasını asenkron ve paralel olarak eğiten, hata toleranslı (retry mekanizmalı) ve eğitim sonunda otomatik grafikli PDF raporu üreten uçtan uca bir AutoML backend servisidir.

## 🛠️ Teknolojiler & Mimariler

* **Backend API:** Python 3.10 & FastAPI
* **İş Kuyruğu & Paralel Çalıştırma:** Celery & Redis
* **Veritabanı:** PostgreSQL & SQLAlchemy ORM
* **AutoML & Makine Öğrenmesi:** Scikit-Learn, Pandas, NumPy
* **Raporlama:** ReportLab & Matplotlib (Türkçe Karakter Destekli)
* **Konteynerleştirme:** Docker & Docker Compose

## 📐 Sistem Mimarisi ve Özellikler

1. **CSV Yükleme & Ön İşleme:** Yüklenen verinin sütun tipleri, eksik değerleri (`NaN`) ve özet istatistikleri otomatik analiz edilir ve temizlenir.
2. **Paralel Model Eğitimi:** `RandomForest`, `GradientBoosting`, `Ridge` / `LogisticRegression` gibi modeller Celery worker'ları üzerinde eş zamanlı olarak eğitilir.
3. **Hata Toleransı (Retry with Backoff):** Eğitim sırasında hata alan model görevleri otomatik olarak 3 kez tekrar denenir.
4. **Grafikli PDF Raporlama:** Eğitim tamamlandığında en iyi modeli öne çıkaran, model performanslarını Bar Grafiği ile görselleştiren PDF raporu otomatik oluşturulur.
5. **CORS Desteği:** React frontend entegrasyonu için ayarlanmıştır.

## 🚀 Kurulum ve Çalıştırma

Projeyi çalıştırmak için bilgisayarınızda **Docker** ve **Docker Compose** kurulu olması yeterlidir.

```bash
# Projeyi klonlayın
git clone <github-repo-url>
cd <repo-klasor-adi>

# Docker konteynırlarını inşa edin ve başlatın
docker compose build
docker compose up -d

Servis çalıştıktan sonra API dokümantasyonuna ve Swagger UI arayüzüne aşağıdaki adresten erişebilirsiniz:
👉 http://localhost:8000/docs