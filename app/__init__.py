import logging
from . import models
from . import keys
from . import auth
from database import db, DB_NAME
from flask import Flask
from os import path

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = keys.API_KEYS['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    with app.app_context():
            db.create_all()

    return app
