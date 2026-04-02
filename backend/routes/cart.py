from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import db
from lib.models import Cart, CartItem, Product
from lib.auth_helpers import get_current_user

cart_bp = Blueprint("cart", __name__)


def get_or_create_cart(user_id):
    """Returns existing cart or creates one if it doesn't exist."""
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart


# ─────────────────────────────────────────
# GET /cart  — view current user's cart
# ─────────────────────────────────────────
@cart_bp.route("/cart", methods=["GET"])
@jwt_required()
def get_cart():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    cart = get_or_create_cart(user.id)

    return jsonify({"cart": cart.to_dict()}), 200


# ─────────────────────────────────────────
# POST /cart/add  — add item to cart
# Body: { "product_id": 1, "quantity": 2 }
# ─────────────────────────────────────────
@cart_bp.route("/cart/add", methods=["POST"])
@jwt_required()
def add_to_cart():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    # Validate inputs
    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    # Check product exists
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Check sufficient stock
    if product.stock < quantity:
        return jsonify({
            "error": f"Insufficient stock. Only {product.stock} units available."
        }), 400

    cart = get_or_create_cart(user.id)

    # If product already in cart, increment quantity
    existing_item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id
    ).first()

    if existing_item:
        new_quantity = existing_item.quantity + quantity
        # Re-check stock against combined quantity
        if product.stock < new_quantity:
            return jsonify({
                "error": f"Cannot add {quantity} more. Only {product.stock - existing_item.quantity} additional units available."
            }), 400
        existing_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
        )
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({
        "message": f"'{product.name}' added to cart",
        "cart": cart.to_dict(),
    }), 200


# ─────────────────────────────────────────
# PATCH /cart/update  — update item quantity
# Body: { "product_id": 1, "quantity": 3 }
# ─────────────────────────────────────────
@cart_bp.route("/cart/update", methods=["PATCH"])
@jwt_required()
def update_cart_item():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or quantity is None:
        return jsonify({"error": "product_id and quantity are required"}), 400

    try:
        quantity = int(quantity)
        if quantity < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Quantity must be a non-negative integer"}), 400

    cart = get_or_create_cart(user.id)

    item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id
    ).first()

    if not item:
        return jsonify({"error": "Item not found in cart"}), 404

    # Setting quantity to 0 removes the item entirely
    if quantity == 0:
        db.session.delete(item)
        db.session.commit()
        return jsonify({
            "message": "Item removed from cart",
            "cart": cart.to_dict(),
        }), 200

    # Check stock
    product = db.session.get(Product, product_id)
    if product.stock < quantity:
        return jsonify({
            "error": f"Only {product.stock} units available."
        }), 400

    item.quantity = quantity
    db.session.commit()

    return jsonify({
        "message": "Cart updated",
        "cart": cart.to_dict(),
    }), 200


# ─────────────────────────────────────────
# DELETE /cart/remove  — remove item from cart
# Body: { "product_id": 1 }
# ─────────────────────────────────────────
@cart_bp.route("/cart/remove", methods=["DELETE"])
@jwt_required()
def remove_from_cart():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    cart = get_or_create_cart(user.id)

    item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id
    ).first()

    if not item:
        return jsonify({"error": "Item not found in cart"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "message": "Item removed from cart",
        "cart": cart.to_dict(),
    }), 200


# ─────────────────────────────────────────
# DELETE /cart/clear  — empty the entire cart
# ─────────────────────────────────────────
@cart_bp.route("/cart/clear", methods=["DELETE"])
@jwt_required()
def clear_cart():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    cart = get_or_create_cart(user.id)

    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()

    return jsonify({
        "message": "Cart cleared",
        "cart": cart.to_dict(),
    }), 200