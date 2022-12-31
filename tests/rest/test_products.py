import json
from flask import url_for

from app import errors, models
from tests.utils import UserFactory, ProductFactory


def test_product_purchase_for_entire_balance(client, db):
    """
    GIVEN a Flask-backed API configured for testing
    WHEN the /product/buy/<int:product_id> endpoint gets a valid req from a user whose balace == product price
    THEN the 'change' field in response is an empty list
    """
    buyer = UserFactory.create(balance=40, role='buyer', db=db)
    vendor = UserFactory.create(role='vendor', db=db)
    product = ProductFactory.create(cost=40, seller_id=vendor.id, db=db)
    # print(buyer)
    # print(product)
    # print(1/0)
    req_json = {"amount": 1}
    response = client.post(
        url_for('api.product_buy_product', product_id=product.id),
        headers={'Authorization': f'Bearer {buyer.token}'},
        json=req_json,
        follow_redirects=True
    )
    response_object = json.loads(response.data)
    print(json.dumps(response_object, indent=2))
    assert response.status_code == 200
    assert response_object['change'] == []

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