"""
Modelos para gerenciamento de investimentos.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
import uuid
from .models import Money


InvestmentType = Literal["renda_fixa", "renda_variavel", "fundo", "criptomoeda", "outro"]


@dataclass(slots=True)
class Investment:
    """Representa um investimento do usuário."""
    name: str
    type: InvestmentType
    initial_amount: Money
    current_amount: Money
    monthly_rate: float  # Taxa de rendimento mensal em decimal (ex: 0.008 = 0.8%)
    user_id: str
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    notes: str = ""
    
    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Nome do investimento obrigatório")
        if self.type not in ("renda_fixa", "renda_variavel", "fundo", "criptomoeda", "outro"):
            raise ValueError("Tipo de investimento inválido")
        if self.initial_amount.amount <= 0:
            raise ValueError("Valor inicial deve ser positivo")
        if self.current_amount.amount < 0:
            raise ValueError("Valor atual não pode ser negativo")
        if not self.user_id or not self.user_id.strip():
            raise ValueError("ID do usuário obrigatório")
    
    @property
    def profit(self) -> Money:
        """Calcula o lucro/prejuízo do investimento."""
        return self.current_amount - self.initial_amount
    
    @property
    def profit_percentage(self) -> float:
        """Calcula a porcentagem de lucro/prejuízo."""
        if self.initial_amount.amount == 0:
            return 0.0
        return float((self.profit.amount / self.initial_amount.amount) * 100)
    
    def to_dict(self) -> dict:
        """Serializa investimento para dicionário."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "initial_amount": self.initial_amount.to_dict(),
            "current_amount": self.current_amount.to_dict(),
            "monthly_rate": self.monthly_rate,
            "user_id": self.user_id,
            "start_date": self.start_date.isoformat(),
            "notes": self.notes,
            "profit": self.profit.to_dict(),
            "profit_percentage": self.profit_percentage,
        }
    
    @staticmethod
    def from_dict(d: dict) -> Investment:
        """Deserializa investimento de dicionário."""
        return Investment(
            id=d["id"],
            name=d["name"],
            type=d["type"],
            initial_amount=Money.from_dict(d["initial_amount"]),
            current_amount=Money.from_dict(d["current_amount"]),
            monthly_rate=d["monthly_rate"],
            user_id=d["user_id"],
            start_date=datetime.fromisoformat(d["start_date"]),
            notes=d.get("notes", ""),
        )

