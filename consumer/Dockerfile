# consumer/Dockerfile (güncel)
FROM python:3.9-slim

WORKDIR /app

# 1) Gerekli Python paketlerini yükleyin
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Uygulama dosyalarını kopyalayın
COPY consumer.py .

# 3) Ortam değişkenleri
ENV KAFKA_BROKER=kafka:9092 \
    KAFKA_TOPIC=projectv1 \
    GROUP_ID=consumer-group-projectv1

# 4) Varsayılan olarak consumer'ı çalıştıracak komut
CMD ["python", "consumer.py"]
