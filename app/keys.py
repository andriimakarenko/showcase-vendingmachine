from . import environment

API_KEYS_DEV = {
    "secret_key": "abracadabra"
}

API_KEYS_PRODUCTION = {
    "secret_key": "abracadabra_but_production"
}

if environment.is_production():
    API_KEYS = API_KEYS_PRODUCTION
else:
    API_KEYS = API_KEYS_DEV
