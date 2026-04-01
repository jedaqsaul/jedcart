from app import app
from db import db
from lib.models import User, Product, Cart
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def seed():
    with app.app_context():
        print("🌱 Clearing old data...")
        db.session.query(Cart).delete()
        db.session.query(User).delete()
        db.session.query(Product).delete()
        db.session.commit()

        print("👤 Creating users...")
        admin = User(
            username="admin",
            email="admin@jedcart.com",
            password_hash=bcrypt.generate_password_hash("admin123").decode("utf-8"),
            is_admin=True,
        )
        user1 = User(
            username="alice",
            email="alice@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
        )
        db.session.add_all([admin, user1])
        db.session.commit()

        print("📦 Creating products...")
        products = [
            Product(name="Wireless Headphones", description="Noise-cancelling over-ear headphones", price=89.99, stock=30, category="Electronics", image_url="https://placehold.co/300x300?text=Headphones"),
            Product(name="Mechanical Keyboard", description="RGB backlit mechanical keyboard", price=59.99, stock=15, category="Electronics", image_url="https://placehold.co/300x300?text=Keyboard"),
            Product(name="Running Shoes", description="Lightweight trail running shoes", price=49.99, stock=50, category="Footwear", image_url="https://placehold.co/300x300?text=Shoes"),
            Product(name="Coffee Mug", description="Double-wall insulated ceramic mug", price=14.99, stock=100, category="Kitchen", image_url="https://placehold.co/300x300?text=Mug"),
            Product(name="Backpack", description="30L waterproof hiking backpack", price=39.99, stock=25, category="Outdoors", image_url="https://placehold.co/300x300?text=Backpack"),
        ]
        db.session.add_all(products)
        db.session.commit()

        print("🛒 Creating cart for alice...")
        cart = Cart(user_id=user1.id)
        db.session.add(cart)
        db.session.commit()

        print("✅ Database seeded successfully!")
        print(f"   Admin login  → admin@jedcart.com / admin123")
        print(f"   User login   → alice@example.com / password123")

if __name__ == "__main__":
    seed()