from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from .models import Transaction, Money, Category
from .repository import ITransactionRepository

class FinanceService:
    def __init__(self, repo: ITransactionRepository):
        self.repo = repo

    def add_transaction(self, *, type: str, amount, description: str, category: str, user_id: str = "default", occurred_at: datetime | None = None) -> Transaction:
        tx = Transaction(
            type=type, amount=Money(amount), description=description,
            category=Category(category), user_id=user_id,
            occurred_at=occurred_at or datetime.now(timezone.utc),
        )
        self.repo.add(tx)
        return tx

    def list_transactions(self, user_id: str | None = None) -> list[Transaction]:
        if user_id:
            transactions = self.repo.list_by_user(user_id)
        else:
            transactions = self.repo.list()
        return sorted(transactions, key=lambda t: t.occurred_at)

    def remove(self, id: str) -> bool:
        return self.repo.remove(id)

    def balance(self, user_id: str | None = None) -> Money:
        total = Money(0)
        transactions = self.repo.list_by_user(user_id) if user_id else self.repo.list()
        for tx in transactions:
            total = total + tx.signed_amount
        return total

    def report(self, group_by: str = "category", user_id: str | None = None) -> dict[str, Money]:
        groups: dict[str, Money] = defaultdict(lambda: Money(0))
        transactions = self.repo.list_by_user(user_id) if user_id else self.repo.list()
        for tx in transactions:
            key = tx.category.name if group_by == "category" else tx.occurred_at.strftime("%Y-%m")
            groups[key] = groups[key] + tx.signed_amount
        return dict(groups)
