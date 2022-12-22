from flask_restx import fields, Namespace

from app import models
from app.rest.utils import make_model


api = Namespace('models')


def get_role(entity):
    return models.Role.query.get(entity.role_id).title


_user_overrides_private = {
    'password': None,
    'role_id': None,
    'role': fields.String(attribute=get_role)
}
user_model_private = make_model(api, models.User, "UserModelPrivate", overrides=_user_overrides_private)

product_model = make_model(api, models.Product, "ProductModel")