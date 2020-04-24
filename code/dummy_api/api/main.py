from flask import Flask, jsonify
from redis import Redis
import os

app = Flask(__name__)
redis = Redis(
    host="redis-service",  # Which host to find the redis-server
    port=4321,  # Which port to find the redis-server
    decode_responses=True
)

@app.route("/")
def describe_redis():

    app_version = os.getenv("VERSION")

    try:
        first_name = redis.get("first-name")
        last_name = redis.get("last-name")
        environment = redis.get("environment")
    except:
        first_name = "ERROR"
        last_name = "ERROR"
        environment = "ERROR"
    
    return jsonify({
        "app-version": app_version,
        "first-name": first_name,
        "last-name": last_name,
        "environment": environment
    })

