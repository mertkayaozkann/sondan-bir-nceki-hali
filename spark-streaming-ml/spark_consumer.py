# spark-streaming-ml/spark_consumer.py
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode
from pyspark.sql.types import StructType, StructField, StringType, FloatType, ArrayType
from pyspark.ml import PipelineModel

# Çevresel değişkenler
KAFKA_BROKER        = os.getenv('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC         = os.getenv('KAFKA_TOPIC',  'projectv1')
CHECKPOINT_LOCATION = os.getenv('CHECKPOINT_LOCATION', 'file:///tmp/spark-checkpoint')
MODEL_PATH          = os.getenv('MODEL_PATH', '/app/model')

def create_spark_session():
    return SparkSession.builder \
        .appName("Weather ML - Inference Stream") \
        .getOrCreate()

def create_schema():
    return StructType([
        StructField("date",        StringType(), True),
        StructField("meantemp",    FloatType(),  True),
        StructField("humidity",    FloatType(),  True),
        StructField("wind_speed",  FloatType(),  True),
        StructField("meanpressure",FloatType(),  True)
    ])

def process_data(df, schema):
    # 1) Mesajın value’sunu JSON array olarak parse et
    array_col = from_json(col("value").cast("string"), ArrayType(schema))
    # 2) Explode ile her öğeyi bir satıra dönüştür, ardından alanları seç
    return df \
        .select(explode(array_col).alias("data")) \
        .select("data.*") \
        .na.drop()

def main():
    spark  = create_spark_session()
    schema = create_schema()

    # A) Model’i yükle
    print(f"✔️ Loading model from {MODEL_PATH}")
    model = PipelineModel.load(MODEL_PATH)

    # B) Kafka’dan stream oku
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    # C) Mesajları parse et
    parsed_df = process_data(kafka_df, schema)

    # D) Her batch için inference
    def foreach_batch(batch_df, batch_id):
        if batch_df.rdd.isEmpty():
            print(f"[Batch {batch_id}] Empty, skipping")
            return

        cnt = batch_df.count()
        print(f"\n📥 Batch {batch_id}: {cnt} records")

        # Tahminleri al
        preds = model.transform(batch_df)

        # İlk 10 sonucu göster
        print(f"📊 Predictions for batch {batch_id}:")
        preds.select("date", "meantemp", "prediction") \
             .show(10, truncate=False)

    # E) Streaming query’i başlat
    query = parsed_df.writeStream \
        .foreachBatch(foreach_batch) \
        .option("checkpointLocation", CHECKPOINT_LOCATION) \
        .outputMode("append") \
        .start()

    print("🚀 Streaming inference started — awaiting data …")
    query.awaitTermination()

if __name__ == "__main__":
    main()
