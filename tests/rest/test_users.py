import json
from flask import url_for

from app import errors, models
from sqlalchemy import func

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

def test_user_delete(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user' URL is gets a DELETE request for an existing user from the same user
    THEN the user record gets deleted
    """
    response = client.delete(
        url_for('api.user_user_details', user_id=1),
        headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoQGV4YW1wbGUuY29tIiwic3ViIjoiYXV0aEBleGFtcGxlLmNvbSIsImF1ZCI6Imh0dHBzOi8vZXhhbXBsZS5jb20iLCJpYXQiOjE2NzE1MTM5NDIsImV4cCI6MTcxNDcxMzk0MiwidXNlcl9pZCI6MX0.vHOp8RyDpm3Jrc-IsK1MY6lLU_SAe9yA_LQuepjup2w'},
        follow_redirects=True
    )
    assert response.status_code == 200

def test_user_delete_unauthenticated(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user' URL is gets a DELETE request for an existing user without a token
    THEN the deletion doesn't happen, 403 is returned
    """
    response = client.delete(
        url_for('api.user_user_details', user_id=1),
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert errors.Errors.MISSING_TOKEN in response_object['errors']
    assert response.status_code == 403

def test_user_patch_unauthorized(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user' URL is gets a DELETE request for an existing user from another user
    THEN the deletion doesn't happen, 403 is returned
    """
    response = client.delete(
        url_for('api.user_user_details', user_id=1),
        headers={'Authorization': 'Bearer invalid_token'},
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert errors.Errors.INVALID_TOKEN in response_object['errors']
    assert response.status_code == 403

def test_user_deposit(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user/deposit/<int:amount>' URL is gets a PUT request from an existing user and the amount is legal
    THEN the user's deposit increases by that amount
    """
    buyer = models.User.query.filter(func.lower(models.User.username) == 'mrbuyer').first()

    response = client.post(
        url_for('api.user_deposit', amount=50),
        headers={'Authorization': f'Bearer {buyer.token}'},
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert response_object['deposit'] == 50
    assert response_object['total_balance'] == 50

    response = client.post(
        url_for('api.user_deposit', amount=50),
        headers={'Authorization': f'Bearer {buyer.token}'},
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert response_object['deposit'] == 50
    assert response_object['total_balance'] == 100

def test_user_deposit_NaN(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user/deposit/<int:amount>' URL is gets a PUT request with a NaN amount
    THEN the corresponging error is thrown
    """
    buyer = models.User.query.filter(func.lower(models.User.username) == 'mrbuyer').first()

    failed_as_expected = False
    try:
        response = client.put(
            url_for('api.user_deposit', amount='abracadabra'),
            headers={'Authorization': f'Bearer {buyer.token}'},
            follow_redirects=True
        )
    except:
        failed_as_expected = True
    assert failed_as_expected

def test_user_deposit_invalid_amount(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the '/user/deposit/<int:amount>' URL is gets a PUT request with an incorrect amount
    THEN the corresponging error is thrown
    """
    buyer = models.User.query.filter(func.lower(models.User.username) == 'mrbuyer').first()

    response = client.post(
        url_for('api.user_deposit', amount=42),
        headers={'Authorization': f'Bearer {buyer.token}'},
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    assert errors.Errors.INVALID_AMOUNT in response_object['errors']
