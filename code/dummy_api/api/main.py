from flask import Flask, jsonify
from redis import Redis

app = Flask(__name__)
redis = Redis(
    host="redis-server",
    port=6379
)

@app.route("/")
def say_hi():
    try:
        first_name = redis.get("first-name")
        last_name = redis.get("last-name")
        environment = redis.get("environment")
    except:
        first_name = "ERROR"
        last_name = "ERROR"
        environment = "ERROR"
    
    return jsonify({
        "first-name": f"{first_name}",
        "last-name": f"{last_name}",
        "environment": f"{environment}"
    })

