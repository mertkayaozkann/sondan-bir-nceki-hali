# Producer Dockerfile (güncel)
FROM python:3.9-slim

# 1. Non-root kullanıcı oluştur
RUN addgroup --system appgroup \
 && adduser  --system --ingroup appgroup appuser

WORKDIR /app

# 2. Gereksinimler
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Uygulama kodu ve test CSV'si
COPY producer.py .
COPY DailyDelhiClimateTest.csv .

# 4. Ortam değişkenleri ile davranışı konfigure et
ENV KAFKA_BROKER=kafka:9092 \
    KAFKA_TOPIC=projectv1 \
    DATA_PATH=DailyDelhiClimateTest.csv \
    CHUNK_SIZE=10 \
    DELAY=1

# 5. Non-root’a geç
USER appuser

# 6. Uygulamayı başlat
CMD ["python", "producer.py"]

