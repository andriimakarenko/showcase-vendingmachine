from werkzeug.security import generate_password_hash

import app.models as models

FAKE_USER_DATA = {
    'username': u'validuser',
    'password': u'password',
    'balance': '0',
    'role': 'buyer'
}

class UserFactory(object):
    @classmethod
    def create(cls, username=None, password=None, balance=None, role=None):
        data = FAKE_USER_DATA.copy()
        if username is None:
            data['username'] = cls.generate_unique_username(data['username'])
        else:
            data['username'] = username
        
        if password is not None:
            data['password'] = password

        if balance is not None:
            data['balance'] = balance
        
        if role is not None:
            data['role'] = role

        user = models.User(
            username=data['username'].lower(),
            password=generate_password_hash(data['password'], method='sha256'),
            balance=data['balance'],
            role_id=models.Role.query.filter_by(title=f'{data["role"]}').first().id
        )

        return user

    @classmethod
    def generate_unique_username(cls, username):
        unique_username = username
        increment = 0

        while models.User.query.filter_by(username=unique_username):
            increment += 1
            unique_username = f"{username}{increment}"

        return unique_username


FAKE_ROLE_DATA = {'title': 'buyer'}

class RoleFactory(object):
    @classmethod
    def create(cls, title=None):
        data = FAKE_ROLE_DATA.copy()
        if title is not None:
            data['title'] = title

        role = models.Role(title=data['title'])
        return role