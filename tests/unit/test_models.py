from app import models

def test_create_role():
    """
    GIVEN a Role model
    WHEN a Role entity is created
    THEN its title is saved correctly
    """

    role = models.Role(title='vendor')
    assert role.title == 'vendor'


def test_create_vendor(vendor_role):
    """
    GIVEN a User model
    WHEN a user with a vendor role is created with custom parameters
    THEN the details are indeed saved correctly
    """

    user = models.User(
        username='testuser',
        password='testpassword',
        balance=100500,
        role_id=vendor_role.id
    )

    assert user.username == 'testuser'
    assert user.password == 'testpassword'
    assert user.balance == 100500
    assert user.role_id == vendor_role.id

def test_create_buyer(buyer_role):
    """
    GIVEN a User model
    WHEN a user with a buyer role is created with custom parameters
    THEN the details are indeed saved correctly
    """

    user = models.User(
        username='testuser',
        password='testpassword',
        balance=1337,
        role_id=buyer_role.id
    )

    assert user.username == 'testuser'
    assert user.password == 'testpassword'
    assert user.balance == 1337
    assert user.role_id == buyer_role.id