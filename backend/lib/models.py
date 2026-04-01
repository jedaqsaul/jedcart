from datetime import datetime
from db import db


# ─────────────────────────────────────────
# USER MODEL
# ─────────────────────────────────────────

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    cart = db.relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<User {self.username}>"


# ─────────────────────────────────────────
# PRODUCT MODEL
# ─────────────────────────────────────────

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(300), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    cart_items = db.relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = db.relationship("OrderItem", back_populates="product")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "image_url": self.image_url,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Product {self.name}>"


# ─────────────────────────────────────────
# CART MODEL
# ─────────────────────────────────────────

class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="cart")
    items = db.relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    @property
    def total(self):
        return round(sum(item.subtotal for item in self.items), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
        }

    def __repr__(self):
        return f"<Cart user_id={self.user_id}>"


# ─────────────────────────────────────────
# CART ITEM MODEL
# ─────────────────────────────────────────

class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Relationships
    cart = db.relationship("Cart", back_populates="items")
    product = db.relationship("Product", back_populates="cart_items")

    @property
    def subtotal(self):
        return round(self.product.price * self.quantity, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "product": self.product.to_dict(),
            "quantity": self.quantity,
            "subtotal": self.subtotal,
        }

    def __repr__(self):
        return f"<CartItem product_id={self.product_id} qty={self.quantity}>"


# ─────────────────────────────────────────
# ORDER MODEL
# ─────────────────────────────────────────

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(50), default="pending")   # pending | confirmed | shipped | delivered | cancelled
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "total_amount": self.total_amount,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Order id={self.id} status={self.status}>"


# ─────────────────────────────────────────
# ORDER ITEM MODEL
# ─────────────────────────────────────────

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)   # snapshot of price at time of order

    # Relationships
    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")

    @property
    def subtotal(self):
        return round(self.unit_price * self.quantity, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "product": self.product.to_dict(),
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": self.subtotal,
        }

    def __repr__(self):
        return f"<OrderItem order_id={self.order_id} product_id={self.product_id}>"