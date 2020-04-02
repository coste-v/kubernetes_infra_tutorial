import argparse
import json
import os
from redis import Redis
from redis.exceptions import ConnectionError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "first_name",
        type=str,
        nargs="?",
        default="Beyond"
    )
    parser.add_argument(
        "last_name",
        type=str,
        nargs="?",
        default="Creation"
    )

    args = parser.parse_args()

    first_name = args.first_name
    last_name = args.last_name
    environment = os.getenv("ENVIRONMENT", "dev")

    redis = Redis(
        host="redis-service",  # Which host to find the redis-server
        port=4321  # Which port to find the redis-server
    )

    try:
        redis.set("first-name", first_name)
        redis.set("last-name", last_name)
        redis.set("environment", environment)
    except ConnectionError:
        print("Not possible to connect to redis-server:6379")
        exit(1)

    exit(0)
