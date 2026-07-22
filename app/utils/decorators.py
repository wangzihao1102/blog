"""Route decorators."""
from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """Decorator that requires the current user to be authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        return f(*args, **kwargs)
    return decorated
