import os

# Hardcoded credentials
SECRET_KEY = "super-secret-123"
DB_PASS = "admin123"

# SQL injection
def get_user(user_id):
    query = "SELECT * FROM users WHERE id=" + user_id
    return db.execute(query)

# Division by zero
def get_average(total, count):
    return total / count

# Unused variable
def process():
    unused = "nothing"
    return True