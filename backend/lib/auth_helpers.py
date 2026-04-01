from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from lib.models import User


def get_current_user():
    """Returns the User object for the currently authenticated user."""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


def admin_required(fn):
    """
    Decorator for routes that require admin privileges.
    Use BELOW @jwt_required().

    Usage:
        @app.route("/admin-only")
        @jwt_required()
        @admin_required
        def admin_route():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper