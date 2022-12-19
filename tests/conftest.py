"""This file is automatically used by pytest to discover global fixtures."""
import pytest
from app.auth.jwt_auth import generate_custom_token

from utils import UserFactory, RoleFactory


# @pytest.fixture
# def user():
#     test_user = UserFactory.create()
#     yield test_user


@pytest.fixture()
def vendor_role():
    role = RoleFactory.create(role='vendor')
    yield role


@pytest.fixture()
def buyer_role():
    role = RoleFactory.create(role='buyer')
    yield role


@pytest.fixture()
def user():
    test_user = UserFactory.create()
    token = generate_custom_token(test_user.id)
    yield test_user, token


@pytest.fixture()
def vendor():
    test_user = UserFactory.create(role='vendor')
    token = generate_custom_token(test_user.id)
    yield test_user, token


@pytest.fixture()
def buyer():
    test_user = UserFactory.create(role='buyer')
    token = generate_custom_token(test_user.id)
    yield test_user, token
