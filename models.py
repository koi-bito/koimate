from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(64))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image_url = db.Column(db.String(256))
    
    # Text combining name, category, and description used for TF-IDF
    features_text = db.Column(db.Text)

class UserBehavior(db.Model):
    __tablename__ = 'user_behavior'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    action_type = db.Column(db.String(32)) # e.g., 'view', 'purchase', 'add_to_cart'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserInput(db.Model):
    __tablename__ = 'user_inputs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    purchases_text = db.Column(db.Text)
    needs_text = db.Column(db.Text)
    shortages_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
