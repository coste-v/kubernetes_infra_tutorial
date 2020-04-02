FROM python:3.8

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

ENV FLASK_APP=api.main.py

# Expose port 5000 (important for the Kube example !)
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=3894"]
