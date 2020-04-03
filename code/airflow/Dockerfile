# Custom Dockerfile
FROM puckel/docker-airflow

USER root
RUN pip install apache-airflow[kubernetes]  # to install the extensions that we need

USER airflow