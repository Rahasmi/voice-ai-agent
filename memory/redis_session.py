import redis

r=redis.Redis(host='localhost',port=6379)

def save_session(session_id,data):
    r.set(session_id,data,ex=1800)

def get_session(session_id):
    return r.get(session_id)