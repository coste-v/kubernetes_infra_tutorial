FROM python:3.8

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Default app version. If not specified in the build, it will be version 1.0
ARG app_version=1.0
ENV VERSION=$app_version

# Expose port 3894 (important for the Kube example !)
CMD ["gunicorn", "--bind", "0.0.0.0:3894", "api.main:app"]
