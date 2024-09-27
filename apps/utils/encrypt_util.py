import jwt

from config.settings import SECRET_KEY


class Encrypt:
    def __init__(self):
        super(Encrypt, self).__init__()

    @staticmethod
    def jwt_encrypt(payload):
        value = jwt.encode(payload, SECRET_KEY, "HS256")
        if type(value) != str:
            value = value.decode("utf-8")
        return value

    @staticmethod
    def jwt_decrypt(payload):
        return jwt.decode(payload, SECRET_KEY, "HS256")
