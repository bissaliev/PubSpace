from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher


class PasswordHelper:
    def __init__(self):
        self.password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))

    def hash(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify(self, plain_password, hashed_password: str) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)
