import os
import sys


TESTING_ENVIRONMENT = 'testing'
DEFAULT_ENVIRONMENT = 'default'


class EnvironmentKeys():
    FLASK_ENV = 'FLASK_ENV'


def is_production():
    if is_testing() or is_development():
        return False
    return True


def is_development():
    return (
        os.getenv(EnvironmentKeys.FLASK_ENV) and
        os.getenv(EnvironmentKeys.FLASK_ENV) == 'development'
    )


def is_testing():
    return "pytest" in sys.modules
