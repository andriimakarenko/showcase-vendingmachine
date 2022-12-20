# showcase-vendingmachine
Showcase API of a vending machine

## Prepequisites
* Python 3.10+
* Poetry

## How to run
    $> poetry install
    $> source "$(poetry env info --path)/bin/activate"
    $> FLASK_DEBUG=1 scripts/start.sh

`FLASK_DEBUG=1` is needed to be able to log in with Swagger

## Swagger
Swagger API is available at `{base_url}/api`

## How to test
    $> source "$(poetry env info --path)/bin/activate"
    $> python -m pytest