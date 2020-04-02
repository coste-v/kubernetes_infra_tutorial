docker build . -t cron_code
docker run -v "/tmp/cron_code:/tmp" -e EXPORT_PATH="/tmp/export.json" -e SECRET_CONFIG="/tmp/secret/config.json" cron_code toto tata --my_flag=tutu

