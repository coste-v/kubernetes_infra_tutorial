from flask import Flask, jsonify
from redis import Redis
import os

app = Flask(__name__)
redis = Redis(
    host="redis-service",  # Host to find the redis-server. Here, the host is a container name and not an IP address!
    port=4321,  # Port to find the redis-server
    decode_responses=True  # Boolean to avoid dealing with bytes instead of strings
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

