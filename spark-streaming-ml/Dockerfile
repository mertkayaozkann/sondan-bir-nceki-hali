 FROM bitnami/spark:3.5.0
 USER root
 RUN apt-get update \
  && apt-get install -y default-jdk \
  && pip3 install --no-cache-dir kafka-python numpy setuptools \
  && rm -rf /var/lib/apt/lists/*

 WORKDIR /app

 COPY model/           ./model/
 COPY spark_consumer.py .
 COPY jars/            ./jars/

 ENV MODEL_PATH=/app/model \
     SPARK_CLASSPATH="/app/jars/*" \
     KAFKA_BROKER="kafka:9092" \
     KAFKA_TOPIC="projectv1" \
     CHECKPOINT_LOCATION="file:///tmp/spark-checkpoint"

CMD ["spark-submit", "--master", "local[*]", "--jars", "/app/jars/*", "/app/spark_consumer.py"]

