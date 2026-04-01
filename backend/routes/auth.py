from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from db import db
from lib.models import User, Cart

auth_bp = Blueprint("auth", __name__)
from app import bcrypt


# ─────────────────────────────────────────
# POST /register
# ─────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # ── Validate required fields ──
    required = ["username", "email", "password"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    username = data["username"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    # ── Check minimum password length ──
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # ── Check for duplicate email or username ──
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    # ── Hash password and create user ──
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )
    db.session.add(new_user)
    db.session.flush()   # flush so new_user.id is available before commit

    # ── Auto-create an empty cart for the new user ──
    cart = Cart(user_id=new_user.id)
    db.session.add(cart)
    db.session.commit()

    # ── Generate JWT token ──
    access_token = create_access_token(identity=str(new_user.id))

    return jsonify({
        "message": "Registration successful",
        "user": new_user.to_dict(),
        "access_token": access_token,
    }), 201


# ─────────────────────────────────────────
# POST /login
# ─────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # ── Look up user by email ──
    user = User.query.filter_by(email=email).first()

    # ── Validate password against stored hash ──
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # ── Generate JWT token ──
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "user": user.to_dict(),
        "access_token": access_token,
    }), 200


# ─────────────────────────────────────────
# GET /me  (protected — requires JWT)
# ─────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200