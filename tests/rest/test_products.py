import json
from flask import url_for

from app import errors, models


def test_product_purchase_for_entire_balance(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the /product/buy/<int:product_id> endpoint gets a valid req from a user whose balace == product price
    THEN the 'change' field in response is an empty list
    """
    pass

def test_product_purchase_insufficient_balance(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the /product/buy/<int:product_id> endpoint gets a valid req from a user whose balace < product price
    THEN the response field 'errors' contains 'INSUFFICIENT_BALANCE' and response code == 403
    """
    pass

def test_product_purchase_change_75(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the /product/buy/<int:product_id> endpoint gets a valid req from a user whose balace exceeds price by 75
    THEN the 'change' field in response is [50, 20, 5]
    """
    pass

def test_product_purchase_change_5(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the /product/buy/<int:product_id> endpoint gets a valid req from a user whose balace exceeds price by 75
    THEN the 'change' field in response is [5]
    """
    pass

def test_product_purchase_change_105(client, seed_database):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the /product/buy/<int:product_id> endpoint gets a valid req from a user whose balace exceeds price by 75
    THEN the 'change' field in response is [100, 5]
    """
    pass