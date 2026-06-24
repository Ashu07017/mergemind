import hashlib
import os

# Hardcoded secret — security issue
JWT_SECRET = "mysecretkey123"

# SQL injection vulnerability
def get_user(username):
    query = "SELECT * FROM users WHERE username='" + username + "'"
    return db.execute(query)

# Division by zero risk
def get_success_rate(success, total):
    return success / total

# Missing error handling
def read_config():
    with open("config.json") as f:
        return f.read()