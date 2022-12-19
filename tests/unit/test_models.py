from app import models

###########
#  ROLES  #
###########

def test_create_role():
    """
    GIVEN a Role model
    WHEN a Role entity is created
    THEN its title is saved correctly
    """

    role = models.Role(title='vendor')
    assert role.title == 'vendor'


###########
#  USERS  #
###########

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


##############
#  PRODUCTS  #
##############

def test_create_product(client, vendor_role, vendor):
    """
    GIVEN a Product model
    WHEN a Product entity is instantiated
    THEN its custom details are saved correctly
    """

    # The fixture vendor returns a tuple, we need the 1st item from it
    vendor = vendor[0]

    product = models.Product(
        product_name='Mitsubishi Eclipse 1G GSX',
        amount_available=42,
        cost=23300,
        seller_id=vendor.id
    )

    assert product.product_name == 'Mitsubishi Eclipse 1G GSX'
    assert product.amount_available == 42
    assert product.cost == 23300
    assert product.seller_id == vendor.id