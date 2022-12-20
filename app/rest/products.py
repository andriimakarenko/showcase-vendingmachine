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
from database import db
from app.errors import Errors, ErrorsForHumans
from app.auth.jwt_auth import (
    generate_custom_auth_token, get_user_id_from_custom_token,
    get_custom_auth_token_from_request
)
from app.rest.utils import (
    make_model, make_model_from_form, make_form_errors_model,
    login_required, conditional_decorator
)


api = Namespace('product', path='/product')


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

product_model = make_model(api, Product, "ProductModel")
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
    "errors": fields.Raw(),
    "form_errors": fields.Nested(buy_form_errors, allow_null=True, skip_none=True),
})


@api.route('')
class AddProduct(Resource):
    @api.expect(add_product_payload)
    @api.doc(security=None)
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
    @api.marshal_with(buy_response_model)
    def get(self, product_id):
        product = User.query.get(product_id)
        if product is None:
            return {
                "errors": [Errors.WRONG_PRODUCT_ID]
            }
        return {
            "product": product
        }, 200
