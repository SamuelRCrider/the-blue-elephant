from functools import wraps
from flask import redirect, session


def login_required(f):
    # decorator for html pages that require user to be logged in
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return wrapper
