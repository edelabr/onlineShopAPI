import os
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()

# Conexión a Redis
IN_DOCKER = os.getenv("IN_DOCKER", "false").lower() == "true"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

redis_client = None
if IN_DOCKER:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

