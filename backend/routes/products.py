from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import db
from lib.models import Product
from lib.auth_helpers import admin_required

products_bp = Blueprint("products", __name__)


# ─────────────────────────────────────────
# GET /products  — list all products
# Public route — no token required
# ─────────────────────────────────────────
@products_bp.route("/products", methods=["GET"])
def get_products():
    # Optional query params: ?category=Electronics&search=keyboard
    category = request.args.get("category")
    search = request.args.get("search")

    query = Product.query

    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.description.ilike(f"%{search}%")
        )

    products = query.order_by(Product.created_at.desc()).all()

    return jsonify({
        "products": [p.to_dict() for p in products],
        "count": len(products),
    }), 200


# ─────────────────────────────────────────
# GET /products/<id>  — single product
# Public route
# ─────────────────────────────────────────
@products_bp.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"product": product.to_dict()}), 200


# ─────────────────────────────────────────
# POST /products  — create product
# Admin only
# ─────────────────────────────────────────
@products_bp.route("/products", methods=["POST"])
@jwt_required()
@admin_required
def create_product():
    data = request.get_json()

    # Validate required fields
    required = ["name", "price"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Validate price is a positive number
    try:
        price = float(data["price"])
        if price <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Price must be a positive number"}), 400

    # Validate stock if provided
    stock = data.get("stock", 0)
    try:
        stock = int(stock)
        if stock < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Stock must be a non-negative integer"}), 400

    product = Product(
        name=data["name"].strip(),
        description=data.get("description", "").strip(),
        price=price,
        stock=stock,
        image_url=data.get("image_url", ""),
        category=data.get("category", "").strip(),
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "message": "Product created successfully",
        "product": product.to_dict(),
    }), 201


# ─────────────────────────────────────────
# PATCH /products/<id>  — update product
# Admin only
# ─────────────────────────────────────────
@products_bp.route("/products/<int:id>", methods=["PATCH"])
@jwt_required()
@admin_required
def update_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()

    # Only update fields that are actually sent
    updatable = ["name", "description", "price", "stock", "image_url", "category"]

    for field in updatable:
        if field in data:
            if field == "price":
                try:
                    val = float(data["price"])
                    if val <= 0:
                        raise ValueError
                    product.price = val
                except (ValueError, TypeError):
                    return jsonify({"error": "Price must be a positive number"}), 400
            elif field == "stock":
                try:
                    val = int(data["stock"])
                    if val < 0:
                        raise ValueError
                    product.stock = val
                except (ValueError, TypeError):
                    return jsonify({"error": "Stock must be a non-negative integer"}), 400
            else:
                setattr(product, field, data[field])

    db.session.commit()

    return jsonify({
        "message": "Product updated successfully",
        "product": product.to_dict(),
    }), 200


# ─────────────────────────────────────────
# DELETE /products/<id>  — delete product
# Admin only
# ─────────────────────────────────────────
@products_bp.route("/products/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": f"Product '{product.name}' deleted successfully"}), 200