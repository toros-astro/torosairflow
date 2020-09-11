# Dockerfile for TOROS Pipeline installation

FROM apache/airflow:1.10.12-python3.7

ENV AIRFLOW_HOME=/toros
ENV AIRFLOW_USER=airflow

USER root

COPY airflow.cfg /toros/airflow.cfg
RUN mkdir -p /toros; \
    mkdir -p /toros/dags; \
    mkdir -p /toros/logs; \
    chown -R airflow:root /toros;

USER airflow

RUN airflow initdb

EXPOSE 8080:5000


# RUN airflow webserver -p 5000 &
# CMD ["airflow", "webserver", "-p", "5000"]
# CMD ["airflow", "scheduler"]
