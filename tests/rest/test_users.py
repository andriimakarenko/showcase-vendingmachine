import json
from flask import url_for

from app import errors

def test_registration_valid(client, seed_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/user' URL is posted to (POST)
    THEN check the response is valid and the user is created and the token is returned
    """
    req_json = {
            "username": "valid_user",
            "password": "password",
            "role": "vendor"
        }
    response = client.post(
        url_for('api.user_sign_up_user'),
        json=req_json,
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert response.status_code == 201
    assert 'user' in response_object
    assert 'token' in response_object and response_object['token'] is not None
    assert response_object['user']['username'] == req_json['username']
    assert response_object['user']['password'] != req_json['password']

def test_registration_username_taken(client, seed_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/user' URL is posted to (POST) with an already taken username
    THEN the response contains an error
    """
    req_json = {
            "username": "MrBuyer",
            "password": "password",
            "role": "buyer"
        }
    response = client.post(
        url_for('api.user_sign_up_user'),
        json=req_json,
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    print(json.dumps(response_object, indent=2))
    assert response.status_code == 400
    assert errors.Errors.USERNAME_TAKEN in response_object['form_errors']['username']