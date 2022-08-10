from flask import redirect, session
from functools import wraps

from sqlalchemy import null


def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def grading(value):
    resultdat = ''
    if 90 <= value <= 100:
        resultdat='A'
    elif 80 <= value <= 89:
        resultdat='B'
    elif 70 <= value <= 79:
        resultdat='c'
    elif 60 <= value <= 69:
        resultdat='D'
    elif 1 <= value <= 59:
        resultdat='F'
    else:
        resultdat = null
    return resultdat