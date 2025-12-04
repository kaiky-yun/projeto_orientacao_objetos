import uuid
from datetime import datetime

class Category:

    __slots__ = ('_id', '_name', '_type', '_user_id', '_created_at')

    def __init__(self, name, type_, user_id, id_=None, created_at=None):
        if not name or not str(name).strip():
            raise ValueError("Nome da categoria não pode ser vazio")
        if type_ not in ['income', 'expense']:
            raise ValueError("Tipo de categoria inválido. Deve ser 'income' ou 'expense'.")
        if not user_id:
            raise ValueError("ID do usuário é obrigatório")

        self._id = id_ if id_ else str(uuid.uuid4())
        self._name = str(name).strip()
        self._type = type_
        self._user_id = user_id
        self._created_at = created_at if created_at else datetime.now().isoformat()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def user_id(self):
        return self._user_id

    @property
    def created_at(self):
        return self._created_at

    def __eq__(self, other):
        if not isinstance(other, Category):
            return False
        return self.id == other.id

    def __repr__(self):
        return f"Category(id='{self.id}', name='{self.name}', type='{self.type}', user_id='{self.user_id}')"

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "user_id": self.user_id,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        return Category(
            id_=data["id"],
            name=data["name"],
            type_=data["type"],
            user_id=data["user_id"],
            created_at=data["created_at"]
        )
