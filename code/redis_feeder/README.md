docker build . -t redis_feeder
docker run -v "/tmp/cron_code:/tmp" -e EXPORT_PATH="/tmp/export.json" -e SECRET_CONFIG="/tmp/secret/config.json" cron_code toto tata --my_flag=tutu

