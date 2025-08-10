from src.exceptions.base import FastAPIUsersException


class UserAlreadyExists(FastAPIUsersException):
    pass


class UserNotExists(FastAPIUsersException):
    pass


class UserAlreadyVerified(FastAPIUsersException):
    pass


class InvalidVerifyToken(FastAPIUsersException):
    pass


class InvalidResetPasswordToken(FastAPIUsersException):
    pass


class InvalidPassword(FastAPIUsersException):
    pass
