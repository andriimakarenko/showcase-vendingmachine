import logging
from os import path
from flask import Flask
from sqlalchemy import select

from config import Config
from database import db, DB_NAME
from app.rest import rest_blueprint
from . import models
from . import keys
from . import auth

def create_app():
    app = Flask(__name__)
    # app.config['SECRET_KEY'] = keys.API_KEYS['secret_key']
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config.from_object(Config)
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

        vendor_id = models.Role.query.filter_by(title='vendor').first().id
        buyer_id = models.Role.query.filter_by(title='buyer').first().id

        the_vendor = models.User(
            username='MrVendor', # This below is a SHA256 of the word 'password'
            password='sha256$Oi393u9gAIBibnzM$d575b373c5b8d037bb404ba828fe0e32322a80b4ddeccdd741ec92621e8378cf',
            balance=0,
            role_id=vendor_id
        )
        rich_buyer = models.User(
            username='MrRichBuyer', # This below is a SHA256 of the word 'buyerpassword'
            password='sha256$mK1fPDEZeKuMwZOY$653a36aa0a32b85de706c9e84158eba6a54df695ab288884ee6471e53abd13b9',
            balance=100500,
            role_id=buyer_id
        )
        broke_buyer = models.User(
            username='MrBeggar',  # This below is a SHA256 of the word 'buyerpassword'
            password='sha256$mK1fPDEZeKuMwZOY$653a36aa0a32b85de706c9e84158eba6a54df695ab288884ee6471e53abd13b9',
            balance=0,
            role_id=buyer_id
        )
        db.session.add_all([the_vendor, rich_buyer, broke_buyer])
        db.session.commit()

        the_insane_stock_product = models.Product(
            product_name='Bubble Gum',
            amount_available=123456789,
            cost=25,
            seller_id=the_vendor.id
        )
        the_low_stock_product = models.Product(
            product_name='Toy Generator',
            amount_available=42,
            cost=70,
            seller_id=the_vendor.id
        )
        the_out_of_stock_product = models.Product(
            product_name='Mitsubishi Eclipse 1G 1:48 model',
            amount_available=0,
            cost=120,
            seller_id=the_vendor.id
        )
        db.session.add_all([the_insane_stock_product, the_low_stock_product, the_out_of_stock_product])
        db.session.commit()

        print('Database seeded')


    @app.cli.command('db_display')
    def db_display():
        all_roles = models.Role.query.all()
        all_users = models.User.query.all()

        print('ROLES')
        for role in all_roles:
            print(role)
        print()

        print('USERS')
        for user in all_users:
            print(user)
        print()

    return app
