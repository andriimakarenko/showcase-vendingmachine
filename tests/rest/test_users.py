import json
from flask import url_for

def test_valid_registration(client, seed_database):
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
    assert False
