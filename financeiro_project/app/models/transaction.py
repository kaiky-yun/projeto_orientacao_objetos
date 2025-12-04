from datetime import datetime, timezone
import uuid
from .money import Money
from .category import Category

class Transaction:

    __slots__ = ('_id', '_type', '_amount', '_description', '_category', '_user_id', '_occurred_at')

    VALID_TYPES = ('income', 'expense')

    def __init__(self, type_, amount, description, category, user_id='default', occurred_at=None, id_=None):

        if type_ not in self.VALID_TYPES:
            raise ValueError(f"Tipo deve ser {' ou '.join(self.VALID_TYPES)}")

        if not isinstance(amount, Money):
            amount = Money(amount)

        if amount.amount <= 0:
            raise ValueError("Valor da transação deve ser positivo")

        if not description or not str(description).strip():
            raise ValueError("Descrição obrigatória")

        if not isinstance(category, Category):
            # Se não for um objeto Category, assumimos que é o nome da categoria
            # e o service deve garantir que é um objeto Category válido.
            # No entanto, para manter a compatibilidade com o from_dict,
            # vamos assumir que o service sempre passa um objeto Category.
            # Se for uma string, é um erro de lógica do service.
            raise TypeError("A categoria deve ser um objeto Category")

        if not user_id or not str(user_id).strip():
            raise ValueError("ID do usuário obrigatório")

        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)
        elif isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at)

        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        self._id = id_ or uuid.uuid4().hex
        self._type = type_
        self._amount = amount
        self._description = str(description).strip()
        self._category = category
        self._user_id = str(user_id).strip()
        self._occurred_at = occurred_at

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def amount(self):
        return self._amount

    @property
    def description(self):
        return self._description

    @property
    def category(self):
        return self._category

    @property
    def user_id(self):
        return self._user_id

    @property
    def occurred_at(self):
        return self._occurred_at

    @property
    def signed_amount(self):
        return self._amount if self._type == 'income' else -self._amount

    def __repr__(self):
        return f"Transaction(type='{self._type}', amount={self._amount}, description='{self._description}')"

    def to_dict(self):
        return {
            "id": self._id,
            "type": self._type,
            "amount": self._amount.to_dict(),
            "description": self._description,
            "category": self._category.to_dict(),
            "user_id": self._user_id,
            "occurred_at": self._occurred_at.isoformat(),
        }

    @staticmethod
    def from_dict(data):
        return Transaction(
            type_=data["type"],
            amount=Money.from_dict(data["amount"]),
            description=data["description"],
            category=Category.from_dict(data["category"]),
            user_id=data.get("user_id", "default"),
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            id_=data["id"],
        )
