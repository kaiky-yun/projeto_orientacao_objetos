from .base import BaseRepository
from ..models import User

class UserRepository(BaseRepository):

    def __init__(self, storage):
        self.storage = storage

    def add(self, user):
        if not isinstance(user, User):
            raise TypeError("Argumento deve ser uma instância de User")

        data = self.storage.load()

        for existing_user in data.values():
            if existing_user['username'] == user.username:
                raise ValueError(f"Username '{user.username}' já existe")
            if existing_user['email'] == user.email:
                raise ValueError(f"Email '{user.email}' já existe")

        data[user.id] = user.to_dict(include_hash=True)
        self.storage.save(data)

    def update(self, user):
        if not isinstance(user, User):
            raise TypeError("Argumento deve ser uma instância de User")

        data = self.storage.load()

        if user.id not in data:
            raise ValueError(f"Usuário com ID '{user.id}' não encontrado")

        data[user.id] = user.to_dict(include_hash=True)
        self.storage.save(data)

    def delete(self, user_id):
        data = self.storage.load()

        if user_id not in data:
            raise ValueError(f"Usuário com ID '{user_id}' não encontrado")

        del data[user_id]
        self.storage.save(data)

    def get_by_id(self, user_id):
        data = self.storage.load()

        if user_id not in data:
            return None

        return User.from_dict(data[user_id])

    def get_by_username(self, username):
        data = self.storage.load()

        for user_data in data.values():
            if user_data['username'] == username:
                return User.from_dict(user_data)

        return None

    def get_by_email(self, email):
        data = self.storage.load()
        email_lower = email.lower()

        for user_data in data.values():
            if user_data['email'].lower() == email_lower:
                return User.from_dict(user_data)

        return None

    def list_all(self):
        data = self.storage.load()
        return [User.from_dict(user_data) for user_data in data.values()]
