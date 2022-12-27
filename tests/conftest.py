"""This file is automatically used by pytest to discover global fixtures."""
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from database import db
from app.auth.jwt_auth import generate_custom_auth_token

from tests.utils import UserFactory, RoleFactory


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture()
def seed_database(client):
    db.create_all()

    # Insert user data
    vendor_role = RoleFactory.create(title='vendor')
    buyer_role = RoleFactory.create(title='buyer')
    db.session.add(vendor_role)
    db.session.add(buyer_role)
    db.session.commit()
    
    # After committing the models will now have ids set

    vendor1 = UserFactory.create(
        username='MrVendor',
        role='vendor'
    )
    vendor2 = UserFactory.create(
        username='MrSecondVendor',
        role='vendor'
    )
    buyer1 = UserFactory.create(
        username='MrBuyer',
        role='buyer'
    )
    buyer2 = UserFactory.create(
        username='MrRichBuyer',
        role='buyer',
        balance=100500
    )
    db.session.add(vendor1)
    db.session.add(vendor2)
    db.session.add(buyer1)
    db.session.add(buyer2)
    db.session.commit()

    for user in [vendor1, vendor2, buyer1, buyer2]:
        user.token = generate_custom_auth_token(user.id)
    
    db.session.add_all([vendor1, vendor2, buyer1, buyer2])
    db.session.commit()

    yield

    db.drop_all()


@pytest.fixture()
def vendor_role():
    role = RoleFactory.create(title='vendor')
    yield role


@pytest.fixture()
def buyer_role():
    role = RoleFactory.create(title='buyer')
    yield role


# @pytest.fixture()
# def user():
#     test_user = UserFactory.create()
#     token = generate_custom_auth_token(test_user.id)
#     yield test_user, token


@pytest.fixture()
def vendor():
    test_user = UserFactory.create(role_id=1)
    token = generate_custom_auth_token(test_user.id)
    yield test_user, token


@pytest.fixture()
def buyer():
    test_user = UserFactory.create(role_id=2)
    token = generate_custom_auth_token(test_user.id)
    yield test_user, token
