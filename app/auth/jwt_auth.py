import logging
import time
import jwt
import jwt.exceptions

from . import auth_constants


def generate_base_jwt_payload(expiry=auth_constants.LOGIN_EXPIRY_TIME, user_id=None):
    payload = {
        'iss': 'auth@example.com',
        'sub': 'auth@example.com',
        'aud': 'https://example.com',
        'iat': int(time.time()),
        'exp': int(time.time() + expiry),
    }

    if user_id:
        payload.update({'user_id': user_id})

    return payload


def get_custom_auth_token_from_request(request):
    """Get our encoded JWT from the request.

    This may be sent in a cookie, header (Auth or Authorization), or POST
    parameter, so we check for them all.
    :param request: the current request object
    :return: the encoded JWT if present, or None
    """
    auth_token = None

    if request.cookies.get(auth_constants.CUSTOM_AUTH_COOKIE_NAME):
        auth_token = request.cookies.get(auth_constants.CUSTOM_AUTH_COOKIE_NAME)
    # Check Authorization header for token
    elif 'Auth' in request.headers:
        auth_token = request.headers['Auth']
    elif request.headers.get("Authorization", "").startswith("Bearer "):
        auth_token = request.headers["Authorization"][7:].strip()
    # Lastly, check post params for token
    elif request.form.get(auth_constants.CUSTOM_AUTH_POST_PARAM_NAME):
        # TODO: check for the presence of the auth token in headers or POST params etc
        auth_token = request.form.get(auth_constants.CUSTOM_AUTH_POST_PARAM_NAME)
    return auth_token


def encode_jwt_payload(payload):
    return jwt.encode(payload, auth_constants.AUTH_SECRET_KEY, algorithm=auth_constants.JWT_ALGORITHM)


def generate_custom_auth_token(user_id):
    payload = generate_base_jwt_payload(user_id=user_id)
    return encode_jwt_payload(payload)


def decode_custom_auth_token(token):
    try:
        return jwt.decode(
            token,
            auth_constants.AUTH_SECRET_KEY,
            audience=auth_constants.JWT_AUDIENCE,
            algorithms=auth_constants.JWT_ALGORITHM,
            options={'verify_exp': False}
        )
    except jwt.exceptions.ExpiredSignatureError:
        logging.info("Rejecting expired JWT login token")
        return None
    except Exception:
        logging.exception("Error decoding JWT login token")
        return None


def get_user_id_from_custom_token(token):
    try:
        payload = decode_custom_auth_token(token)
        # Don't check the expiry time of tokens for now
        if not payload or not payload['user_id']:
            return None
        return int(payload['user_id'])
    except Exception:
        logging.exception("Error getting user from decoded JWT token")
