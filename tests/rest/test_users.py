def test_create_vendor_with_fixture(vendor):
    assert vendor.username == 'validuser'
    assert vendor.password != 'password'