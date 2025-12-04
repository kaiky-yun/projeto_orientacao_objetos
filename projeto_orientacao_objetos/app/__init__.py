from flask import Flask
from flask_caching import Cache
from config import config
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config.from_object(config.get(config_name, config['default']))

    cache = Cache(app)

    from app.controllers import auth_bp, transaction_bp, investment_bp, report_bp, category_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(category_bp)

    app.cache = cache

    return app
