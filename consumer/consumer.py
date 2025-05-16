import os
import json
import time
from kafka import KafkaConsumer

# Ortam değişkenleri üzerinden Kafka ayarları
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC  = os.environ.get('KAFKA_TOPIC', 'projectv1')
GROUP_ID     = os.environ.get('GROUP_ID', 'consumer-group-projectv1')

def create_consumer():
    try:
        return KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            group_id=GROUP_ID,
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    except Exception as e:
        print(f"Kafka consumer oluşturulurken hata: {e}")
        exit(1)

if __name__ == '__main__':
    consumer = create_consumer()
    print(f"✔️  Connected to Kafka broker at {KAFKA_BROKER}")
    print(f"📥 Listening on topic `{KAFKA_TOPIC}` in group `{GROUP_ID}`…\n")

    try:
        for msg in consumer:
            batch = msg.value
            # batch’in bir liste olup olmadığını kontrol edelim
            if isinstance(batch, list):
                print(f"\n💡 Yeni batch geldi: {len(batch)} kayıt")
                for i, record in enumerate(batch, start=1):
                    # Kaydı satır satır yazdır
                    print(f"  {i}. {record}")
            else:
                # Eski tek-satır format kalırsa
                print(f"\n💡 Yeni tekil mesaj: {batch}")
    except KeyboardInterrupt:
        print("\n🛑 Consumer durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
    finally:
        # Consumer’ı kapat
        try:
            consumer.close()
        except:
            pass
