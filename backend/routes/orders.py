from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import db
from lib.models import Cart, CartItem, Order, OrderItem
from lib.auth_helpers import get_current_user, admin_required

orders_bp = Blueprint("orders", __name__)


# ─────────────────────────────────────────
# POST /orders  — place an order from cart
# ─────────────────────────────────────────
@orders_bp.route("/orders", methods=["POST"])
@jwt_required()
def place_order():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    cart = Cart.query.filter_by(user_id=user.id).first()

    if not cart or not cart.items:
        return jsonify({"error": "Your cart is empty"}), 400

    # ── Validate all items have sufficient stock before touching DB ──
    stock_errors = []
    for item in cart.items:
        if item.product.stock < item.quantity:
            stock_errors.append(
                f"'{item.product.name}': only {item.product.stock} in stock, "
                f"you requested {item.quantity}"
            )

    if stock_errors:
        return jsonify({
            "error": "Some items are out of stock",
            "details": stock_errors,
        }), 400

    # ── Create the order ──
    total = cart.total

    order = Order(
        user_id=user.id,
        total_amount=total,
        status="pending",
    )
    db.session.add(order)
    db.session.flush()  # get order.id before commit

    # ── Snapshot each cart item into an order item ──
    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.product.price,  # price snapshot
        )
        db.session.add(order_item)

        # Deduct stock
        item.product.stock -= item.quantity

    # ── Clear the cart after order is placed ──
    CartItem.query.filter_by(cart_id=cart.id).delete()

    db.session.commit()

    return jsonify({
        "message": "Order placed successfully",
        "order": order.to_dict(),
    }), 201


# ─────────────────────────────────────────
# GET /orders  — get current user's orders
# ─────────────────────────────────────────
@orders_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    orders = Order.query.filter_by(user_id=user.id)\
        .order_by(Order.created_at.desc()).all()

    return jsonify({
        "orders": [o.to_dict() for o in orders],
        "count": len(orders),
    }), 200


# ─────────────────────────────────────────
# GET /orders/<id>  — get single order
# ─────────────────────────────────────────
@orders_bp.route("/orders/<int:id>", methods=["GET"])
@jwt_required()
def get_order(id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    order = db.session.get(Order, id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Users can only view their own orders; admins can view any
    if order.user_id != user.id and not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify({"order": order.to_dict()}), 200


# ─────────────────────────────────────────
# PATCH /orders/<id>/status  — update order status
# Admin only
# Body: { "status": "shipped" }
# ─────────────────────────────────────────
@orders_bp.route("/orders/<int:id>/status", methods=["PATCH"])
@jwt_required()
@admin_required
def update_order_status(id):
    order = db.session.get(Order, id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json()
    new_status = data.get("status")

    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        return jsonify({
            "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }), 400

    order.status = new_status
    db.session.commit()

    return jsonify({
        "message": f"Order status updated to '{new_status}'",
        "order": order.to_dict(),
    }), 200


# ─────────────────────────────────────────
# GET /admin/orders  — all orders (admin only)
# ─────────────────────────────────────────
@orders_bp.route("/admin/orders", methods=["GET"])
@jwt_required()
@admin_required
def get_all_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify({
        "orders": [o.to_dict() for o in orders],
        "count": len(orders),
    }), 200