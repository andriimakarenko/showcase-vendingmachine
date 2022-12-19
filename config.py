import os

from app import keys
from database import DB_NAME

# Determine the folder of the top-level directory of this project
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False
    SECRET_KEY = keys.API_KEYS['secret_key']
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'


class ProductionConfig(Config):
    FLASK_ENV = 'production'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}_test'

