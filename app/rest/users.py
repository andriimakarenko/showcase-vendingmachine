import jwt
import datetime
import uuid
import re
import os
from flask import jsonify, request, make_response
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, PasswordField, RadioField, validators
from sqlalchemy import func

from app.models import User, Role
from database import db
from app.errors import Errors, ErrorsForHumans
from app.auth.jwt_auth import generate_custom_auth_token
from app.rest.utils import (
    make_model, make_model_from_form, make_form_errors_model,
    login_required, conditional_decorator
)


api = Namespace('user', path='/user')


USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")

username_validators = [
    validators.Regexp(USERNAME_REGEX, message=Errors.INVALID_USERNAME),
    validators.Length(min=4, max=25, message=Errors.INVALID_LENGTH),
]

username_field = StringField('Username',
    username_validators + [validators.InputRequired(message=Errors.REQUIRED_FIELD)],
)

token_field = StringField('AuthCode',
    [validators.InputRequired(message=Errors.REQUIRED_FIELD)],
)

password_field = PasswordField('Password', [
    validators.Length(min=8, max=1000, message="Password must be at least 8 characters long"),
    validators.InputRequired(message=Errors.REQUIRED_FIELD),
])

status_field = RadioField(
    'Status',
    choices=[('vendor', 'Vendor'), ('buyer', 'Buyer')],
)


class SignUpForm(Form):
    username = username_field
    password = password_field
    status = status_field

class LoginForm(Form):
    username = username_field
    password = password_field

# TODO: Add user model with password cut out and return that instead of user_model
user_model = make_model(api, User, "UserModel")
sign_up_payload = make_model(api, SignUpForm)
log_in_payload = make_model(api, LoginForm)
login_form_errors = make_form_errors_model(api, LoginForm)
login_response_model = api.model("LoginResponseModel", {
    "user": fields.Nested(user_model, allow_null=True),
    "token": fields.String(allow_null=True),
    "errors": fields.Raw(),
    "form_errors": fields.Nested(login_form_errors, allow_null=True, skip_none=True),
})


@api.route('')
class CreateUser(Resource):
    @api.expect(sign_up_payload)
    @api.doc(security=None)
    @api.marshal_with(user_model)
    def post(self):
        data = request.get_json() 
        hashed_password = generate_password_hash(data['password'], method='sha256')
        
        user = User(
            username=data['username'],
            password=hashed_password,
            balance=0,
            role_id=Role.query.filter_by(title=f'{data["role"]}').first().id
        )
        db.session.add(user)
        db.session.commit()
        token = generate_custom_auth_token(user.id)
        return {
            "user": user,
            "token": token,
        }, 201


@api.route('/login')
class LogInUser(Resource):
    @conditional_decorator(api.expect(log_in_payload), os.environ.get('FLASK_DEBUG'))
    @api.doc(security=None)
    @api.marshal_with(login_response_model)
    def post(self):
        """
        Validate a user's login details and return an auth token on success.
        Note that I only use @except on this method in development environment, not in production.
        That is because it leaks passwords in error messages, which is not acceptibel in production.
        Yet without this expect you can't test the method with Swagger.
        """
        form = LoginForm.from_json(api.payload)

        user = User.query.filter(func.lower(User.username) == func.lower(form.data["username"])).first()

        if (
            not user or
            not check_password_hash(user.password, form.data["password"])
        ):
            return {
                "form_errors": {
                    "username": [Errors.INVALID_LOGIN],
                    "password": [Errors.INVALID_LOGIN]
                }
            }, 400

        return {
            "token": generate_custom_auth_token(user.id),
            "user": user,
        }, 200


# Only enable this endpoint in DEV env. It's clearly unsecure to give out in PROD
@conditional_decorator(api.route('/all_users'), os.environ.get('FLASK_DEBUG'))
class GetAllUsers(Resource):
    @login_required
    def get(self):
        users = User.query.all()
        result = []  
        for user in users:  
            user_data = {}  
            user_data['id'] = user.id 
            user_data['username'] = user.username
            user_data['role'] = Role.query.get(user.role_id).title

            result.append(user_data)  
        return jsonify({'users': result})