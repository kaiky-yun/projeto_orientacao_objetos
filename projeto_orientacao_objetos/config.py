import os
from datetime import timedelta

class Config:

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    DATA_DIR = os.path.expanduser('~/.financeiro_app')
    USERS_DB_PATH = os.path.join(DATA_DIR, 'users.json')
    TRANSACTIONS_DB_PATH = os.path.join(DATA_DIR, 'transactions.json')
    INVESTMENTS_DB_PATH = os.path.join(DATA_DIR, 'investments.json')
    CATEGORIES_DB_PATH = os.path.join(DATA_DIR, 'categories.json')

    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True
    DATA_DIR = '/tmp/financeiro_app_test'
    USERS_DB_PATH = os.path.join(DATA_DIR, 'users.json')
    TRANSACTIONS_DB_PATH = os.path.join(DATA_DIR, 'transactions.json')
    INVESTMENTS_DB_PATH = os.path.join(DATA_DIR, 'investments.json')
    CATEGORIES_DB_PATH = os.path.join(DATA_DIR, 'categories.json')

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
