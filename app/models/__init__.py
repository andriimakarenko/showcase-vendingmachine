# The ORM models go gere


from database import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    users = db.relationship('User', backref='roles')

    def __repr__(self) -> str:
        return f'<id: {self.id}, title: {self.title}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    token = db.Column(db.String(160), nullable=True)
    balance = db.Column(db.Integer)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    products = db.relationship('Product', backref='users')

    def __repr__(self) -> str:
        return (
            f'<id: {self.id}, '
            f'username: {self.username}, '
            f'balance: {self.balance}, '
            f'role_id: {self.role_id}>'
        )


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(160)),
    amount_available = db.Column(db.Integer),
    cost = db.Column(db.Integer),
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self) -> str:
        return (
            f'<product_name: {self.product_name}, '
            f'amount_available: {self.amount_available}, '
            f'cost: {self.cost}>'
            f'seller_id: {self.seller_id}>'    
        )