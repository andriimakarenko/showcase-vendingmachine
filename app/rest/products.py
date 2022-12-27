import jwt
import datetime
import uuid
import re
import os
from flask import jsonify, request, make_response
from flask_restx import Namespace, Resource, fields
from wtforms import Form, StringField, PasswordField, RadioField, validators, IntegerField
from sqlalchemy import func, delete

from app.models import User, Role, Product
from app.rest.rest_models import product_model
from database import db
from app.errors import Errors, ErrorsForHumans
from app.auth.jwt_auth import (
    generate_custom_auth_token, get_user_id_from_custom_token,
    get_custom_auth_token_from_request
)
from app.rest.utils import (
    make_model, make_model_from_form, make_form_errors_model,
    login_required, conditional_decorator, BSTNode, build_change
)


api = Namespace('product', path='/product')


coin_values = [20, 5, 10, 50, 100]
coin_bst = BSTNode()
for val in coin_values:
    coin_bst.insert(val)


product_name_validators = [
    validators.Length(min=4, max=25, message=Errors.INVALID_LENGTH),
]

product_name_field = StringField('Username',
    product_name_validators + [validators.InputRequired(message=Errors.REQUIRED_FIELD)],
)
cost_field = IntegerField('Price')
product_amount_field = IntegerField('Amount')


class AddProductForm(Form):
    name = product_name_field
    cost = cost_field
    amount = product_amount_field

class BuyForm(Form):
    amount = product_amount_field


add_product_payload = make_model(api, AddProductForm)
add_product_form_errors = make_form_errors_model(api, AddProductForm)
add_product_response_model = api.model("AddProductResponse", {
    "product": fields.Nested(product_model),
    "errors": fields.Raw(),
    "form_errors": fields.Nested(add_product_form_errors, allow_null=True, skip_none=True),
})

buy_payload = make_model(api, BuyForm)
buy_form_errors = make_form_errors_model(api, BuyForm)
buy_response_model = api.model("BuyResponse", {
    "product": fields.Nested(product_model),
    "amount_purchased": fields.Integer(),
    "transaction_amount": fields.Integer(),
    "change": fields.List(fields.Integer),
    "errors": fields.Raw(),
    "form_errors": fields.Nested(buy_form_errors, allow_null=True, skip_none=True),
})

product_details_model = api.model("ProductDetails", {
    "product": fields.Nested(product_model),
    "errors": fields.Raw(),
    "form_errors": fields.Nested(buy_form_errors, allow_null=True, skip_none=True),
})


@api.route('')
class AddProduct(Resource):
    @api.expect(add_product_payload)
    @api.marshal_with(add_product_response_model)
    @login_required
    def post(self):
        data = request.get_json()

        token = get_custom_auth_token_from_request(request)
        user_id = get_user_id_from_custom_token(token)
        role_id = User.query.get(user_id).role_id
        role = Role.query.get(role_id)
        if role.title != 'vendor':
            return {
                "errors": [Errors.NOT_VENDOR]
            }, 403
        
        product = Product(
            product_name=data['name'],
            cost=data['cost'],
            amount_available=data['amount'],
            seller_id=user_id
        )
        db.session.add(product)
        db.session.commit()

        return {
            "product": product
        }, 201


@api.route('/<int:product_id>')
class ProductDetails(Resource):
    @api.marshal_with(product_details_model)
    def get(self, product_id):
        product = Product.query.get(product_id)
        if product is None:
            return {
                "errors": [Errors.WRONG_PRODUCT_ID]
            }, 404
        return {
            "product": product
        }, 200
    
    @login_required
    @api.marshal_with(product_details_model)
    def patch(self, product_id):
        if not request.headers or 'Authorization' not in request.headers:
            return {
                "errors": [Errors.MISSING_TOKEN]
            }, 403
        product = Product.query.get(product_id)
        if product is None:
            return {
                "errors": [Errors.WRONG_PRODUCT_ID]
            }, 404

        owner_id = product.seller_id
        token = get_custom_auth_token_from_request(request)
        internal_user_id = get_user_id_from_custom_token(token)
        if not internal_user_id or internal_user_id != owner_id:
            return {
                "errors": [Errors.ACCESS_DENIED]
            }, 403
        data = request.get_json()
        if 'name' in data:
            product.product_name = data['name']
        if 'cost' in data:
            product.cost = data['cost']
        if 'amount' in data:
            product.amount_available = data['amount']
        db.session.add(product)
        db.session.commit()

        return {
            "product": product
        }, 200

    # Would actually do a soft-delete in real world project.
    # I'd add a DATE deleted_at field, and actually delete the record once so much time passed,
    # that GDPR would require the deletion
    @login_required
    def delete(self, product_id):
        if not request.headers or 'Authorization' not in request.headers:
            return {
                "errors": [Errors.MISSING_TOKEN]
            }, 403
        product = Product.query.get(product_id)
        if product is None:
            return {
                "errors": [Errors.WRONG_PRODUCT_ID]
            }, 404

        owner_id = product.seller_id
        token = get_custom_auth_token_from_request(request)
        internal_user_id = get_user_id_from_custom_token(token)
        if not internal_user_id or internal_user_id != owner_id:
            return {
                "errors": [Errors.ACCESS_DENIED]
            }, 403
        sql = delete(Product).where(product.id == product_id)
        db.session.execute(sql)
        db.session.commit()

        return 204


@api.route('/buy/<int:product_id>')
class BuyProduct(Resource):
    @api.expect(buy_payload)
    @api.marshal_with(buy_response_model)
    @login_required
    def post(self, product_id):
        if not request.headers or 'Authorization' not in request.headers:
            return {
                "errors": [Errors.MISSING_TOKEN]
            }, 403
        token = get_custom_auth_token_from_request(request)
        user_id = get_user_id_from_custom_token(token)
        if not user_id:
            return {
                "errors": [Errors.INVALID_TOKEN]
            }, 403
        buyer = User.query.get(user_id)
        
        product = Product.query.get(product_id)
        if product is None:
            return {
                "errors": [Errors.WRONG_PRODUCT_ID]
            }, 404
        
        seller = User.query.get(product.seller_id)

        amount = request.get_json()['amount']
        transaction_amount = product.cost * amount
        if type(amount) != int:
            return {
                "errors": [Errors.NAN_PRODUCT_AMOUNT]
            }
        if buyer.balance < transaction_amount:
            return {
                "errors": [Errors.INSUFFICIENT_FUNDS]
            }, 403
        if product.amount_available < amount:
            return {
                "errors": [Errors.NOT_ENOUGH_STOCK]
            }, 400

        buyer.balance -= transaction_amount
        seller.balance += transaction_amount
        product.amount_available -= amount

        change = build_change(buyer.balance, coin_bst)
        return {
            "product": product,
            "amount_purchased": amount,
            "transaction_amount": transaction_amount,
            "change": change
        }, 200
