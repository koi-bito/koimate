from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints (to be created)
    from routes.auth import auth_bp
    from routes.recommender import recommender_bp
    from routes.analytics import analytics_bp
    from routes.tracking import tracking_bp
    from routes.pages import pages_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(recommender_bp, url_prefix='/api/recommend')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(tracking_bp, url_prefix='/api/track')
    app.register_blueprint(pages_bp)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
