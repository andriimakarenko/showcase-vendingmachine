# coding=utf-8


class Errors(object):
    ACCESS_DENIED = "ACCESS_DENIED"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_TOKEN = "INVALID_TOKEN"
    INVALID_USERNAME = "INVALID_USERNAME"
    INVALID_LENGTH = "INVALID_LENGTH"
    REQUIRED_FIELD = "REQUIRED_FIELD"
    INVALID_LOGIN = "INVALID_LOGIN"
    USERNAME_TAKEN = "USERNAME_TAKEN"
    MISSING_TOKEN = "MISSING_TOKEN"
    NAN_DEPOSIT = "NAN_DEPOSIT"
    INVALID_AMOUNT = "INVALID_AMOUNT"


class ErrorsForHumans(object):
    ACCESS_DENIED = "Access denied."
    INVALID_REQUEST = "Invalid request."
    INVALID_TOKEN = "Invalid token"
    INVALID_USERNAME = "Please provide a valid username"
    INVALID_LENGTH = "This field must be between 4 and 25 chars long" # Yes, I know I set this in 2 diff places
    REQUIRED_FIELD = "This field is required"
    INVALID_LOGIN = "Your login or password was incorrect, please tyr again"
    USERNAME_TAKEN = "Sorry but this username is already taken"
    MISSING_TOKEN = "Sorry, your request needs a token"
    NAN_DEPOSIT = "Sorry, you can only deposit a whole number of cents, specifically 5, 10, 20, 50, or 100"
    INVALID_AMOUNT = "Sorry, you can only deposit 5, 10, 20, 50, or 100 cents"