from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from config.setup import Config
from db import db

# Extension instances (no app bound yet)
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    with app.app_context():
        from lib import models 
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    # Register route blueprints
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.users import users_bp
    from routes.orders import orders_bp
    from routes.cart import cart_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(cart_bp)

    # Health check route
    @app.route("/")
    def index():
        return {"message": "JedCart API is running 🛒"}, 200

    return app

# Entry point
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)