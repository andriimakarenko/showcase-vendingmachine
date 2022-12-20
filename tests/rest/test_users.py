import json
from flask import url_for

from app import errors

def test_user_registration_valid(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
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
    # print(json.dumps(response_object, indent=2))
    assert response.status_code == 201
    assert 'user' in response_object
    assert 'token' in response_object and response_object['token'] is not None
    assert response_object['user']['username'] == req_json['username']
    assert response_object['user']['password'] != req_json['password']

def test_user_registration_username_taken(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
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
    # print(json.dumps(response_object, indent=2))
    assert response.status_code == 400
    assert errors.Errors.USERNAME_TAKEN in response_object['form_errors']['username']

def test_user_get_details(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user' URL is gets a GET request for an existing user from an authenticated user
    THEN the user details are returned
    """
    response = client.get(
        url_for('api.user_user_details', user_id=1),
        headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoQGV4YW1wbGUuY29tIiwic3ViIjoiYXV0aEBleGFtcGxlLmNvbSIsImF1ZCI6Imh0dHBzOi8vZXhhbXBsZS5jb20iLCJpYXQiOjE2NzE1MTM5NDIsImV4cCI6MTcxNDcxMzk0MiwidXNlcl9pZCI6MX0.vHOp8RyDpm3Jrc-IsK1MY6lLU_SAe9yA_LQuepjup2w'},
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert 'user' in response_object
    assert response_object['user']['username'] == 'mrvendor'

def test_user_get_details_unauthorized(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user' URL is gets a GET request for an existing user from an authenticated user
    THEN the user details are returned
    """
    response = client.get(
        url_for('api.user_user_details', user_id=1),
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert response.status_code == 403
    assert errors.Errors.MISSING_TOKEN in response_object['errors']

def test_user_patch(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user' URL is gets a PATCH request for an existing user from the same user
    THEN the user details are updated
    """
    req_json = {"username": "MrNewVendor"}
    response = client.patch(
        url_for('api.user_user_details', user_id=1),
        headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoQGV4YW1wbGUuY29tIiwic3ViIjoiYXV0aEBleGFtcGxlLmNvbSIsImF1ZCI6Imh0dHBzOi8vZXhhbXBsZS5jb20iLCJpYXQiOjE2NzE1MTM5NDIsImV4cCI6MTcxNDcxMzk0MiwidXNlcl9pZCI6MX0.vHOp8RyDpm3Jrc-IsK1MY6lLU_SAe9yA_LQuepjup2w'},
        json=req_json,
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert 'user' in response_object
    assert response_object['user']['username'] == 'MrNewVendor'

def test_user_patch_unauthenticated(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user' URL is gets a PATCH request for an existing user from the same user
    THEN the user details are updated
    """
    req_json = {"username": "MrNewVendor"}
    response = client.patch(
        url_for('api.user_user_details', user_id=1),
        json=req_json,
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert errors.Errors.MISSING_TOKEN in response_object['errors']
    assert response.status_code == 403

def test_user_patch_unauthorized(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user' URL is gets a PATCH request for an existing user from the same user
    THEN the user details are updated
    """
    req_json = {"username": "MrNewVendor"}
    response = client.patch(
        url_for('api.user_user_details', user_id=1),
        headers={'Authorization': 'Bearer invalid_token'},
        json=req_json,
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert errors.Errors.INVALID_TOKEN in response_object['errors']
    assert response.status_code == 403