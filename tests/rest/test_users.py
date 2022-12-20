from flask import url_for

def test_valid_registration(client, seed_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST)
    THEN check the response is valid and the user is logged in
    """
    response = client.post(
        url_for('api.user_user'),
        data={
            "username": "validuser",
            "password": "password",
            "role": "vendor"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert False
