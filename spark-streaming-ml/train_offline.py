# spark-streaming-ml/train_offline.py
import os
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml import Pipeline

def main():
    # 1) SparkSession oluştur
    spark = SparkSession.builder \
        .appName("Weather Offline Training") \
        .getOrCreate()

    # 2) Eğitim verisini oku
    train_path = os.environ.get("TRAIN_DATA_PATH", "DailyDelhiClimateTrain.csv")
    df = (
        spark.read
             .csv(train_path, header=True, inferSchema=True)
             .na.drop()
    )
    count = df.count()
    print(f"✅ Eğitim verisi yüklendi: {count} kayıt")

    # 3) Özellikleri hazırla
    feature_cols = ["humidity", "wind_speed", "meanpressure"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

    # 4) Model tanımı
    lr = LinearRegression(featuresCol="features", labelCol="meantemp")

    # 5) Pipeline ve eğitim
    pipeline = Pipeline(stages=[assembler, lr])
    model = pipeline.fit(df)
    print("🎉 Model başarıyla eğitildi.")

    # 6) Modeli kaydet
    out_dir = os.environ.get("MODEL_OUTPUT_PATH", "model")
    model.write().overwrite().save(out_dir)
    print(f"💾 Model `{out_dir}` klasörüne kaydedildi.")

    spark.stop()

if __name__ == "__main__":
    main()
