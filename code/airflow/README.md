
# Build the container

docker build . -t my-airflow

# Run the container

docker run -d -p 8080:8080 -v $(pwd)/dags:/usr/local/airflow/dags -v /Users/vcoste/.kube/config:/home/airflow/docker_desktop_config my-airflow webserver

# Connect to Airflow UI

http://localhost:8080/admin/
