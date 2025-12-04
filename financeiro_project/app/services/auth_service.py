from ..models import User

class AuthService:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register(self, username, email, password):

        if not password or len(password) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")

        password_hash = User.hash_password(password)

        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            password_hash=password_hash
        )

        self.user_repository.add(user)

        return user

    def login(self, username_or_email, password):

        user = self.user_repository.get_by_username(username_or_email)

        if not user:
            user = self.user_repository.get_by_email(username_or_email.lower())

        if user and user.verify_password(password):
            return user

        return None

    def get_user_by_id(self, user_id):
        return self.user_repository.get_by_id(user_id)

    def get_user_by_username(self, username):
        return self.user_repository.get_by_username(username)

    def get_user_by_email(self, email):
        return self.user_repository.get_by_email(email)

    def list_all_users(self):
        return self.user_repository.list_all()
