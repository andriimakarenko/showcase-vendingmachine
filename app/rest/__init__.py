# APIs to be connected TO here

import collections
import json
import logging
import re

import wtforms_json
from flask import Blueprint
from flask.wrappers import Response  # pylint: disable=unused-import
from flask_restx import Api
from werkzeug.exceptions import BadRequest

from app.rest.rest_models import api as rest_models_api
from app.rest.users import api as users_api
from app.rest.products import api as products_api

# Monkey-patch support for JSON into WTForms
wtforms_json.init()

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
    }
}

rest_blueprint = Blueprint('api', __name__, url_prefix='/api')
rest_api = Api(
    rest_blueprint,
    title='Vending machine API',
    version='0.1.0',
    security=['apikey'],
    authorizations=authorizations,
    validate=True,
)

rest_api.add_namespace(rest_models_api)
rest_api.add_namespace(users_api)
rest_api.add_namespace(products_api)

@rest_blueprint.after_request
def after_request(response):
    """
    :param Response response:
    :rtype: Response
    """
    # Catch all types of errors as in no situation should trying to make the errors nicer break the API
    try:
        if response.headers.get('Content-Type') == 'application/json':
            response_data = json.loads(response.get_data())

            if response_data is None:
                return response

            form_errors = response_data.get('form_errors')  # This might not exist, might be None, or a dict

            if form_errors:
                for field_name, errors in form_errors.items():
                    # Swap u'foo' is too short to 'foo' is too short
                    new_errors = [re.sub(r"^u'", "'", error) for error in errors]
                    response_data['form_errors'][field_name] = new_errors

            response.set_data(json.dumps(response_data))

    except Exception:
        logging.exception('Error modifying form errors')

    response.headers.add('Access-Control-Allow-Origin', '*')  # TODO: Restrict this to our web domain?
    response.headers.add('Access-Control-Allow-Methods', 'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT')
    response.headers.add('Access-Control-Allow-Headers', 'Accept, Authorization, Content-Type')
    return response
