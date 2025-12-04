from datetime import datetime, timezone
import uuid
import bcrypt

class User:

    __slots__ = ('_id', '_username', '_email', '_password_hash', '_created_at')

    def __init__(self, username, email, password_hash, id_=None, created_at=None):

        if not username or not str(username).strip():
            raise ValueError("Nome de usuário obrigatório")

        if not email or not str(email).strip():
            raise ValueError("Email obrigatório")

        if "@" not in str(email):
            raise ValueError("Email inválido")

        if not password_hash or not str(password_hash).strip():
            raise ValueError("Hash de senha obrigatório")

        self._id = id_ or uuid.uuid4().hex
        self._username = str(username).strip()
        self._email = str(email).strip().lower()
        self._password_hash = str(password_hash).strip()
        self._created_at = created_at or datetime.now(timezone.utc)

    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    @property
    def email(self):
        return self._email

    @property
    def password_hash(self):
        return self._password_hash

    @property
    def created_at(self):
        return self._created_at

    def verify_password(self, password):
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self._password_hash.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def hash_password(password):
        if not password or len(password) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")

        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def __repr__(self):
        return f"User(username='{self._username}', email='{self._email}')"

    def to_dict(self, include_hash=False):
        data = {
            "id": self._id,
            "username": self._username,
            "email": self._email,
            "created_at": self._created_at.isoformat(),
        }

        if include_hash:
            data["password_hash"] = self._password_hash

        return data

    @staticmethod
    def from_dict(data):
        return User(
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"],
            id_=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )
