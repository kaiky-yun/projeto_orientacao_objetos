from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
import uuid
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


TransactionType = Literal["income", "expense"]


class Money:
    """Value Object para valores monetários com Decimal (2 casas)."""
    __slots__ = ("_amount",)

    def __init__(self, amount: Decimal | int | float | str):
        try:
            value = amount if isinstance(amount, Decimal) else Decimal(str(amount))
        except (InvalidOperation, ValueError) as e:
            raise ValueError("Valor monetário inválido") from e
        self._amount = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def amount(self) -> Decimal:
        return self._amount

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        return Money(self.amount - other.amount)

    def __neg__(self) -> "Money":
        return Money(-self.amount)

    def __mul__(self, other) -> "Money":
        return Money(self.amount * Decimal(str(other)))

    def __repr__(self) -> str:
        return f"Money({str(self.amount)})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Money) and self.amount == other.amount

    def to_dict(self) -> dict:
        return {"amount": str(self.amount)}

    @staticmethod
    def from_dict(d: dict) -> "Money":
        return Money(Decimal(d["amount"]))


@dataclass(slots=True)
class Category:
    name: str
    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Categoria não pode ser vazia")


@dataclass(slots=True)
class Transaction:
    type: TransactionType
    amount: Money
    description: str
    category: Category
    user_id: str = "default"  # ID do usuário proprietário
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def __post_init__(self):
        if self.type not in ("income", "expense"):
            raise ValueError("Tipo deve ser 'income' ou 'expense'")
        if self.amount.amount <= 0:
            raise ValueError("Valor da transação deve ser positivo")
        if not self.description or not self.description.strip():
            raise ValueError("Descrição obrigatória")

    @property
    def signed_amount(self) -> Money:
        return self.amount if self.type == "income" else -self.amount

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "amount": self.amount.to_dict(),
            "description": self.description,
            "category": {"name": self.category.name},
            "user_id": self.user_id,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @staticmethod
    def from_dict(d: dict) -> "Transaction":
        return Transaction(
            id=d["id"],
            type=d["type"],
            amount=Money.from_dict(d["amount"]),
            description=d["description"],
            category=Category(d["category"]["name"]),
            user_id=d.get("user_id", "default"),  # Compatibilidade com dados antigos
            occurred_at=datetime.fromisoformat(d["occurred_at"]),
        )
