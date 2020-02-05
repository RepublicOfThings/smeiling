from models import User


CREDS = [{"username": "bob", "password": "bob"}, {"username": "bill", "password": "bill"}]
USERS = [User(**creds) for creds in CREDS]


def get_user(user, users=None):
    for _user in users or USERS:
        if _user.id == user:
            return _user
