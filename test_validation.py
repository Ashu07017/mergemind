DB_PASSWORD = "supersecret123"

def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def divide(a, b):
    return a / b

def process(data):
    x = data["value"]
    y = data["count"]

    total = x / y

    return total