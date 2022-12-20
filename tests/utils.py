from werkzeug.security import generate_password_hash

import app.models as models

FAKE_USER_DATA = {
    'username': 'validuser',
    'password': generate_password_hash('password', method='sha256'),
    'balance': '0',
    'role_id': '0'
}

class UserFactory(object):
    @classmethod
    def create(cls, username=None, password=None, balance=None, role=None, role_id=None):
        data = FAKE_USER_DATA.copy()

        if username is None:
            data['username'] = cls.generate_unique_username(data['username'])
        else:
            data['username'] = username
        
        if password is not None:
            data['password'] = password

        if balance is not None:
            data['balance'] = balance

        if role_id is not None:
            data['role_id'] = role_id
        elif role is not None:
            data['role_id'] = models.Role.query.filter_by(title=role).first().id

        user = models.User(
            username=data['username'].lower(),
            password=generate_password_hash(data['password'], method='sha256'),
            balance=data['balance'],
            role_id=data['role_id']
        )

        return user

    @classmethod
    def generate_unique_username(cls, username):
        unique_username = username
        increment = 0

        while models.User.query.filter_by(username=unique_username).first():
            increment += 1
            unique_username = f"{username}{increment}"

        return unique_username


FAKE_ROLE_DATA = {'title': 'buyer'}

class RoleFactory(object):
    @classmethod
    def create(cls, id=None, title=None):
        data = FAKE_ROLE_DATA.copy()

        if title is not None:
            data['title'] = title

        role = models.Role(title=data['title'])
        return role