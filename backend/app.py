from flask import Flask, jsonify
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
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",   
                "http://127.0.0.1:5173",
            ],
            "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"error": "Missing or invalid token. Please log in."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired. Please log in again."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Token is invalid."}), 422

    



    

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

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3NTA3MjczNSwianRpIjoiZmM2NTBkMGQtY2M3ZC00ZjM4LTg5NDYtNGM4NDgzNTc2OWExIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3NzUwNzI3MzUsImNzcmYiOiJjYTBiYzZlNy1iNTVhLTQ5MGUtODlkOC1hMDYxOTAwZWQyNjMiLCJleHAiOjE3NzU2Nzc1MzV9._HpeS4yWVSDBRP1VA9HcjN5JlXOK-FjfAUun2Fa6wUg