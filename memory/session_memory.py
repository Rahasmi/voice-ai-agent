session_memory = {}

def get_session(user_id):
    if user_id not in session_memory:
        session_memory[user_id] = {}
    return session_memory[user_id]

def set_context(user_id, key, value):
    session = get_session(user_id)
    session[key] = value

def get_context(user_id, key):
    session = get_session(user_id)
    return session.get(key)