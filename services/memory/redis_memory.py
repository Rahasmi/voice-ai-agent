import redis
import json

# connect to redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def save_message(session_id, role, message):
    key = f"chat:{session_id}"

    data = {
        "role": role,
        "message": message
    }

    r.rpush(key, json.dumps(data))


def get_messages(session_id):
    key = f"chat:{session_id}"

    messages = r.lrange(key, 0, -1)

    return [json.loads(m) for m in messages]