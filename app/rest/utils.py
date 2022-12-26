import logging
from flask import request
from flask_restx import Model, Namespace, fields
# from flask_restx import fields as flask_fields, Resource, ValidationError
from app.keys import API_KEYS
from wtforms import Form, fields as wtforms_fields
# from wtforms.validators import Length as LengthValidator
from functools import wraps

from app.models import User
from app.auth.jwt_auth import get_custom_auth_token_from_request, get_user_id_from_custom_token
from app.errors import Errors, ErrorsForHumans
from database import db


class AuthError(Exception):
    """Authentication error"""
    pass


class APIError(Exception):
    def __init__(self, message, errors, status_code=400, *args):
        args = (message,) + args
        super(APIError, self).__init__(*args)
        self.status_code = status_code
        self.errors = errors


class BSTNode:
    def __init__(self, val=None):
        self.left = None
        self.right = None
        self.val = val

    def insert(self, val):
        if not self.val:
            self.val = val
            return

        if self.val == val:
            return

        if val < self.val:
            if self.left:
                self.left.insert(val)
                return
            self.left = BSTNode(val)
            return

        if self.right:
            self.right.insert(val)
            return
        self.right = BSTNode(val)

    def greatest_lte_val(self, val):
        """
        Find and return the greatest value in the BST
        that is less than or equal to the given value.
        """
        # if self.val == val or \
        #   (self.left.val < val and self.right.val > val):
        #     return self.val

        if self.val > val:
            if not self.left:
                return None
            if self.left.val <= val:
                return self.left.val
            return self.left.greatest_lte_val(val)

        if self.val < val:
            if (not self.right) or (self.right.val > val):
                return self.val
            return self.right.greatest_lte_val(val)

        return self.val


def build_change(amount, coin_bst):
    result = []

    dollars = amount % 100
    if dollars:
        # append 100 to list n times
        pass

    while amount > 0:
        coin = coin_bst.greatest_lte_val(amount)
        result.append(coin)
        amount -= coin

    return result


def conditional_decorator(decorator, condition, *args):

    def wrapper(function):
        if condition:
            return decorator(function)
        else:
            return function

    return wrapper


def get_id(entity):
    """Get ID from an entity"""
    return (entity.id if isinstance(entity, db.Model) else entity["id"]) or 0


def get_logged_in_user(token):
    """Try to get the logged in user or throw"""
    if not token:
        raise AuthError(Errors.MISSING_TOKEN)
    user_id = get_user_id_from_custom_token(token)
    if not user_id:
        raise AuthError(Errors.INVALID_TOKEN)

    user = User.query.get(user_id)
    if not user:
        raise AuthError(Errors.INVALID_TOKEN)
    return user


# def login_optional(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         try:
#             token = get_custom_auth_token_from_request(request)
#             user = get_logged_in_user(token)
#             request.user_id = user.id
#             request.user = user
#         except AuthError:
#             request.user_id = None
#             request.user = None
#         return f(*args, **kwargs)
#     return wrapper


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            token = get_custom_auth_token_from_request(request)
            user = get_logged_in_user(token)
            request.user_id = user.id
            request.user = user
        except AuthError as e:
            return {"errors": [str(e)]}, 403
        return f(*args, **kwargs)
    return wrapper


def make_model_from_form(api, form_class, name=None, overrides=None):
    field_map = {
        wtforms_fields.BooleanField: fields.Boolean,
        wtforms_fields.FieldList: fields.List,
        wtforms_fields.IntegerField: fields.Integer,
        wtforms_fields.PasswordField: fields.String,
        wtforms_fields.StringField: fields.String,
        wtforms_fields.TextAreaField: fields.String,
    }
    form = form_class()
    model_fields = overrides.copy() if overrides else {}
    for field in form:
        if field.name in model_fields:
            # Ignore model fields that were passed into this method
            continue
        field_args = []
        field_kwargs = {
            'required': field.flags.required,
        }
        field_type = field_map.get(type(field), None)
        if field_type is None:
            logging.error(
                "No field type mapping for %s.%s (%s), using String fallback",
                form_class.__name__,
                field.name,
                type(field),
            )
            field_type = fields.String
        elif field_type is fields.List:
            inner_field_type = field_map.get(field.unbound_field.field_class, None)
            if inner_field_type is None:
                logging.error(
                    "No field type mapping for inner field of %s.%s (%s), using String fallback",
                    form_class.__name__,
                    field.name,
                    type(field.unbound_field.field_class),
                )
                inner_field_type = fields.String,
            field_args.append(inner_field_type)
        model_fields[field.name] = field_type(*field_args, **field_kwargs)
    # Remove any fields that are explicitly set to None
    model_fields = {
        name: value
        for name, value in model_fields.items()
        if value is not None
    }
    return api.model(name or form_class.__name__, model_fields)



def make_form_errors_model(api, form_class, model_name=None, remap=None):
    """Automatically make a Flask-RESTPlus model representing the errors for a WTForms class.

    :param Namespace api: Flask-RESTPlus Namespace instance
    :param type form_class: A WTForms class
    :param str model_name: Optional name for the generated model
    :param dict remap: Used to rename fields (such as user_email to email_address)
    :return: Auto-generated model representing the possible errors from form_class
    :rtype: Model

    >>> from action.users import ProfileForm
    >>> from flask_restx import Namespace
    >>> api = Namespace("my_namespace")
    >>> profile_form_errors_model = make_form_errors_model(api, ProfileForm, remap={
    >>>     "user_email": "email_address",
    >>> })
    """
    if model_name is None:
        model_name = "{0}Errors".format(form_class.__name__)
    if remap is None:
        remap = {}
    model_fields = {}
    for field in form_class():
        field_name = remap.get(field.name, field.name)
        model_fields[field_name] = fields.List(fields.String(), allow_null=True)
    model_fields = {
        key: value
        for key, value in model_fields.items()
        if value is not None
    }
    return api.model(model_name, model_fields)


def vuild_model_from_db_model(api, model_class, model_name=None, overrides=None):
    property_map = {
        db.Float: fields.Float,
        db.Integer: fields.Integer,
        db.String: fields.String,
    }
    model_fields = overrides.copy() if overrides else {}
    if "id" not in model_fields:
        model_fields["id"] = fields.Integer(required=True, attribute=get_id)

    for field in model_class.__table__.columns.values():
        field_name = field.name
        field_type = field.type
        property_type = property_map.get(field_type)

        if property_type is None:
            logging.error(f"Unexpected db field type {field_type}")
            property_type = fields.String

        # Ignore model fields that were explicitly specified in overrides.
        if field_name in model_fields:
            if model_fields[field_name] is None:
                continue

        model_fields[field_name] = property_type
    # Remove any fields that are explicitly set to None
    return {
        field_name: value
        for field_name, value in model_fields.items()
        if value is not None
    }


def make_model_from_db_model(api, model_class, model_name=None, overrides=None):
    model_fields = vuild_model_from_db_model(api, model_class, overrides)
    return api.model(model_name or model_class.__name__, model_fields)


def make_model(api, cls, name=None, overrides=None):
    if issubclass(cls, Form):
        return make_model_from_form(api, cls, name, overrides)
    if issubclass(cls, db.Model):
        return make_model_from_db_model(api, cls, name, overrides)
    raise TypeError("Unexpected type: {0}".format(cls.__name__))