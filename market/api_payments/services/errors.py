from random import choice


class ValidationError(Exception):
    msg = "Something went wrong"
    pass


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class VerificationFailed(Exception):
    pass


class TooManyRequests(Exception):
    pass


class DoNotHaveEnoughMoney(Exception):
    pass


def get_random_error():
    """Получить случайную ошибку"""
    errors = (
        ValidationError("The data is not valid"),
        AuthorizationError("Not enough rights"),
        AuthenticationError("Could not to pass authorization"),
        VerificationFailed("Could not to connect"),
        TooManyRequests("Server is excessive"),
        DoNotHaveEnoughMoney("Do not have enough money"),
    )
    return choice(errors)
