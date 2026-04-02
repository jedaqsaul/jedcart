from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import db
from lib.models import User
from lib.auth_helpers import get_current_user, admin_required

users_bp = Blueprint("users", __name__)


# ─────────────────────────────────────────
# GET /profile  — get own profile
# ─────────────────────────────────────────
@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200


# ─────────────────────────────────────────
# PATCH /profile  — update own profile
# Body: { "username": "newname" }
# ─────────────────────────────────────────
@users_bp.route("/profile", methods=["PATCH"])
@jwt_required()
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if "username" in data:
        new_username = data["username"].strip()
        if not new_username:
            return jsonify({"error": "Username cannot be empty"}), 400
        existing = User.query.filter_by(username=new_username).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "Username already taken"}), 409
        user.username = new_username

    if "email" in data:
        new_email = data["email"].strip().lower()
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "Email already in use"}), 409
        user.email = new_email

    db.session.commit()
    return jsonify({
        "message": "Profile updated",
        "user": user.to_dict(),
    }), 200


# ─────────────────────────────────────────
# GET /admin/users  — list all users
# Admin only
# ─────────────────────────────────────────
@users_bp.route("/admin/users", methods=["GET"])
@jwt_required()
@admin_required
def get_all_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        "users": [u.to_dict() for u in users],
        "count": len(users),
    }), 200


# ─────────────────────────────────────────
# DELETE /admin/users/<id>  — delete a user
# Admin only
# ─────────────────────────────────────────
@users_bp.route("/admin/users/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.is_admin:
        return jsonify({"error": "Cannot delete an admin user"}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"User '{user.username}' deleted"}), 200