import os
from typing import Optional


def get_user_safely(user_id: int, db_connection) -> Optional[dict]:
    """Fetch a user by ID using a parameterized query."""
    query = "SELECT * FROM users WHERE id = %s"
    return db_connection.execute(query, (user_id,))


def safe_divide(a: float, b: float) -> float:
    """Divide two numbers, raising a clear error on zero division."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b