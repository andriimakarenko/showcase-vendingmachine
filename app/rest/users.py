import jwt
import datetime
import uuid
import re
from flask import jsonify, request, make_response
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, PasswordField, validators

from app.models import User
from database import db
from app.errors import Errors, ErrorsForHumans
from app.auth.jwt_auth import generate_custom_auth_token
from app.rest.utils import make_model, make_model_from_form, make_form_errors_model


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


class LoginForm(Form):
    username = username_field
    password = password_field


user_model = make_model(api, User, "UserModel")
login_form_errors = make_form_errors_model(api, LoginForm)
login_response_model = api.model("LoginResponseModel", {
    "user": fields.Nested(user_model, allow_null=True),
    "token": fields.String(allow_null=True),
    "errors": fields.Raw(),
    "form_errors": fields.Nested(login_form_errors, allow_null=True, skip_none=True),
})


@api.route('')
class CreateUser(Resource):
    def post(self): 
        data = request.get_json() 
        hashed_password = generate_password_hash(data['password'], method='sha256')
        
        new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
        db.session.add(new_user) 
        db.session.commit()   
        return jsonify({'message': 'registered successfully'})


@api.route("")
class LogInUser(Resource):
    @api.doc(security=None)
    @api.marshal_with(login_response_model)
    def post(self):
        """Validate a user's login details and return an auth token on success.

        Note that we deliberately do *not* use @expect on this method since that causes password leakage in errors.
        """
        form = LoginForm.from_json(api.payload)

        user = User.query(User.username == form.data["login_id"].lower()).get()

        if (
            not user or
            not check_password_hash(form.data["password"], user.password)
        ):
            return {
                "form_errors": {
                    "login_id": [Errors.INVALID_LOGIN],
                    "password": [Errors.INVALID_LOGIN]
                }
            }, 400

        return {
            "token": generate_custom_auth_token(user.key.id()),
            "user": user,
        }, 200

# This is some stupid boilerplate code from Internet that I hoped would work but it doesn't
# @api.route('/login', methods=['POST']) 
# def login_user():
#     auth = request.authorization  
#     if not auth or not auth.username or not auth.password: 
#        return make_response('Could not log in', 401, {'Authentication': 'Login and passwod required"'})   
 
#     user = User.query.filter_by(name=auth.username).first()  
#     if check_password_hash(user.password, auth.password):
#         token = jwt.encode({
#                 'public_id' : user.public_id,
#                 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)
#             }, keys.API_KEYS['secret_key'], "HS256"
#         )
 
#         return jsonify({'token' : token})
 
#     return make_response('Could not log in',  401, {'Authentication': 'Login or password incorrect'})


@api.route('/all_users')
class GetAllUsers():
    def get(self):    
        users = User.query.all()
        result = []  
        for user in users:  
            user_data = {}  
            user_data['public_id'] = user.public_id 
            user_data['name'] = user.name
            user_data['password'] = user.password
            user_data['admin'] = user.admin

            result.append(user_data)  
        return jsonify({'users': result})