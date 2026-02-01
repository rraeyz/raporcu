FROM python:3.11-slim

WORKDIR /app

# Gerekli paketleri yükle
COPY requirements_web.txt .
RUN pip install --no-cache-dir -r requirements_web.txt

# Uygulama dosyalarını kopyala
COPY . .

# Gereksiz dosyaları temizle
RUN mkdir -p temp audio_files
RUN rm -rf __pycache__ *.bat

# Uygulama portunu açığa çıkar
EXPOSE 5000

# Web uygulamasını başlat
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "web_app:app"]
