# Builds a plain pip-installed PySpark image rather than depending on a
# prebuilt Spark distribution image - bitnami/spark no longer publishes any
# tags at all (Bitnami restructured their catalog), and this sidesteps that
# entirely. eclipse-temurin publishes multi-arch (amd64 + arm64) manifests,
# so this also works unmodified on an Arm VPS (e.g. Oracle Cloud's Ampere A1).
FROM eclipse-temurin:17-jre-jammy

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir pyspark==3.5.1

WORKDIR /opt/spark-app
COPY streaming_job.py .

CMD ["python3", "streaming_job.py"]
