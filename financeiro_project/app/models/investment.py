from datetime import datetime, timezone
import uuid
from .money import Money

class Investment:

    __slots__ = ('_id', '_name', '_type', '_initial_amount', '_current_amount', '_monthly_rate', '_user_id', '_start_date', '_notes')

    VALID_TYPES = ('renda_fixa', 'renda_variavel', 'fundo', 'criptomoeda', 'outro')

    def __init__(self, name, type_, initial_amount, current_amount, monthly_rate, user_id, start_date=None, notes='', id_=None):

        if not name or not str(name).strip():
            raise ValueError("Nome do investimento obrigatório")

        if type_ not in self.VALID_TYPES:
            raise ValueError(f"Tipo deve ser um de: {', '.join(self.VALID_TYPES)}")

        if not isinstance(initial_amount, Money):
            initial_amount = Money(initial_amount)

        if not isinstance(current_amount, Money):
            current_amount = Money(current_amount)

        if initial_amount.amount <= 0:
            raise ValueError("Valor inicial deve ser positivo")

        if current_amount.amount < 0:
            raise ValueError("Valor atual não pode ser negativo")

        if not user_id or not str(user_id).strip():
            raise ValueError("ID do usuário obrigatório")

        try:
            monthly_rate = float(monthly_rate)
        except (ValueError, TypeError):
            raise ValueError("Taxa mensal deve ser um número")

        if start_date is None:
            start_date = datetime.now(timezone.utc)
        elif isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)

        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)

        self._id = id_ or uuid.uuid4().hex
        self._name = str(name).strip()
        self._type = type_
        self._initial_amount = initial_amount
        self._current_amount = current_amount
        self._monthly_rate = monthly_rate
        self._user_id = str(user_id).strip()
        self._start_date = start_date
        self._notes = str(notes).strip() if notes else ''

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
    def initial_amount(self):
        return self._initial_amount

    @property
    def current_amount(self):
        return self._current_amount

    @property
    def monthly_rate(self):
        return self._monthly_rate

    @property
    def user_id(self):
        return self._user_id

    @property
    def start_date(self):
        return self._start_date

    @property
    def notes(self):
        return self._notes

    @property
    def profit(self):
        return self._current_amount - self._initial_amount

    @property
    def profit_percentage(self):
        if self._initial_amount.amount == 0:
            return 0.0
        return float((self.profit.amount / self._initial_amount.amount) * 100)

    def __repr__(self):
        return f"Investment(name='{self._name}', type='{self._type}', current={self._current_amount})"

    def to_dict(self):
        return {
            "id": self._id,
            "name": self._name,
            "type": self._type,
            "initial_amount": self._initial_amount.to_dict(),
            "current_amount": self._current_amount.to_dict(),
            "monthly_rate": self._monthly_rate,
            "user_id": self._user_id,
            "start_date": self._start_date.isoformat(),
            "notes": self._notes,
            "profit": self.profit.to_dict(),
            "profit_percentage": self.profit_percentage,
        }

    @staticmethod
    def from_dict(data):
        return Investment(
            name=data["name"],
            type_=data["type"],
            initial_amount=Money.from_dict(data["initial_amount"]),
            current_amount=Money.from_dict(data["current_amount"]),
            monthly_rate=data["monthly_rate"],
            user_id=data["user_id"],
            start_date=datetime.fromisoformat(data["start_date"]),
            notes=data.get("notes", ""),
            id_=data["id"],
        )
