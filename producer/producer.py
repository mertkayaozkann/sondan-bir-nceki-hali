import pandas as pd
import json
import time
from kafka import KafkaProducer
import os
import sys

# Kafka ayarları (env’den okunuyor)
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'projectv1')
DATA_PATH = os.environ.get('DATA_PATH', 'DailyDelhiClimateTest.csv')
CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 10))
DELAY = float(os.environ.get('DELAY', 1.0))

def create_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except Exception as e:
        print(f"Kafka producer oluşturulurken hata: {e}")
        sys.exit(1)

def stream_test_data():
    try:
        reader = pd.read_csv(DATA_PATH, parse_dates=['date'], chunksize=CHUNK_SIZE)
    except Exception as e:
        print(f"Test CSV okuma hatası: {e}")
        sys.exit(1)

    producer = create_producer()
    batch_num = 0

    for chunk in reader:
        batch_num += 1
        # Her chunk bir list of dict
        records = []
        for _, row in chunk.iterrows():
            records.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'meantemp': float(row['meantemp']),
                'humidity': float(row['humidity']),
                'wind_speed': float(row['wind_speed']),
                'meanpressure': float(row['meanpressure'])
            })

        producer.send(KAFKA_TOPIC, records)
        print(f"[Batch {batch_num}] Gönderilen kayıt sayısı: {len(records)}")
        time.sleep(DELAY)

    # Stream bittiğinde pod’u canlı tutmak için sonsuz döngü
    print("Tüm batch’ler gönderildi, producer ayakta kalıyor...")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    print(f"KAFKA_BROKER={KAFKA_BROKER}")
    print(f"KAFKA_TOPIC={KAFKA_TOPIC}")
    print(f"DATA_PATH={DATA_PATH}")
    print(f"CHUNK_SIZE={CHUNK_SIZE}, DELAY={DELAY}s")
    try:
        stream_test_data()
    except KeyboardInterrupt:
        print("Producer durduruldu.")
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit(1)
