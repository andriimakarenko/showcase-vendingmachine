import logging
from flask import Flask
from os import path
from sqlalchemy import select

from . import models
from . import keys
from . import auth
from database import db, DB_NAME
from app.rest import rest_blueprint

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = keys.API_KEYS['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    with app.app_context():
            db.create_all()

    app.register_blueprint(rest_blueprint)

    @app.cli.command('db_create')
    def db_create():
        db.create_all()
        print('Database created')


    @app.cli.command('db_drop')
    def db_drop():
        db.drop_all()
        print('Database dropped')


    @app.cli.command('db_seed')
    def db_seed():
        vendor = models.Role(title='vendor')
        buyer = models.Role(title='buyer')
        db.session.add_all([vendor, buyer])
        db.session.commit()
        print(vendor.title)
        print()

        vendor_request = select(models.Role).where(models.Role.title == 'vendor')
        vendor_id = db.session.execute(vendor_request).first().id
        print(vendor_id)
        print()
        print()
        buyer_id = select(models.Role).where(models.Role.title == 'buyer').id

        the_vendor = models.User(username='MrVendor', # This below is a SHA256 of the word 'password'
                                password='sha256$Oi393u9gAIBibnzM$d575b373c5b8d037bb404ba828fe0e32322a80b4ddeccdd741ec92621e8378cf',
                                balance=0,
                                role_id=vendor_id)
        rich_buyer = models.User(username='MrBuyer',
                                password='sha256$Oi393u9gAIBibnzM$d575b373c5b8d037bb404ba828fe0e32322a80b4ddeccdd741ec92621e8378cf',
                                balance=100500,
                                role_id=buyer_id)
        broke_buyer = models.User(username='MrBeggar',
                                password='sha256$Oi393u9gAIBibnzM$d575b373c5b8d037bb404ba828fe0e32322a80b4ddeccdd741ec92621e8378cf',
                                balance=0,
                                role_id=buyer_id)
        db.session.add_all([the_vendor, rich_buyer, broke_buyer])
        db.session.commit()
        print('Database seeded')

    return app
