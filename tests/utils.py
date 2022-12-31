from werkzeug.security import generate_password_hash

from app import models
from app.auth.jwt_auth import generate_custom_auth_token
# from database import db

FAKE_USER_DATA = {
    'username': 'validuser',
    'password': generate_password_hash('password', method='sha256'),
    'balance': '0',
    'role_id': '0'
}

class UserFactory():
    @classmethod
    def create(cls, username=None, password=None, balance=None, role=None, role_id=None, db=None):
        data = FAKE_USER_DATA.copy()

        if username is None:
            data['username'] = cls.generate_unique_username(data['username'])
        else:
            data['username'] = username

        if password is not None:
            data['password'] = password

        if balance is not None:
            data['balance'] = balance

        if role_id is not None:
            data['role_id'] = role_id
        elif role is not None:
            data['role_id'] = RoleFactory.get_or_create(title=role, db=db).id

        user = models.User(
            username=data['username'].lower(),
            password=generate_password_hash(data['password'], method='sha256'),
            balance=data['balance'],
            role_id=data['role_id']
        )

        if db is not None:
            db.session.add(user)
            db.session.commit()
            token = generate_custom_auth_token(user.id)
            user.token = token
            db.session.add(user)
            db.session.commit()

        return user

    @classmethod
    def generate_unique_username(cls, username):
        unique_username = username
        increment = 0

        while models.User.query.filter_by(username=unique_username).first():
            increment += 1
            unique_username = f"{username}{increment}"

        return unique_username


FAKE_ROLE_DATA = {'title': 'buyer'}

class RoleFactory():
    @classmethod
    def create(cls, title=None, db=None):
        data = FAKE_ROLE_DATA.copy()

        if title is not None:
            data['title'] = title

        role = models.Role(title=data['title'])

        if db is not None:
            db.session.add(role)
            db.session.commit()

        return role

    @classmethod
    def get_or_create(cls, title, db=None):
        role = models.Role.query.filter_by(title=title).first()
        if not role:
            role = cls.create(title=title, db=db)

        return role


FAKE_PRODUCT_DATA = {
    'product_name': 'validname',
    'amount_available': 100,
    'cost': 5,
    'seller_id': 1,
}

class ProductFactory():
    @classmethod
    def create(cls, product_name=None, amount_available=None, cost=None, seller_id=None, db=None):
        data = FAKE_PRODUCT_DATA.copy()

        if product_name is None:
            data['product_name'] = product_name

        if amount_available is not None:
            data['amount_available'] = amount_available

        if cost is not None:
            data['cost'] = cost

        if seller_id is not None:
            data['seller_id'] = seller_id
        else:
            vendor_role_id = RoleFactory.get_or_create(title='vendor', db=db).id
            first_vendor = models.User.query.filter_by(role_id=vendor_role_id).first()
            data['seller_id'] = first_vendor.id

        product = models.Product(
            product_name=data['product_name'],
            amount_available=data['amount_available'],
            cost=data['cost'],
            seller_id=data['seller_id']
        )

        if db is not None:
            db.session.add(product)
            db.session.commit()

        return product
