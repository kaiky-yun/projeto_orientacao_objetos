from finance.services import FinanceService
from finance.repository import ITransactionRepository
from finance.models import Transaction, Money, Category
from typing import Iterable, Optional


class MemRepo(ITransactionRepository):
    def __init__(self):
        self.items: list[Transaction] = []

    def list(self) -> list[Transaction]:
        return list(self.items)

    def by_id(self, id: str) -> Optional[Transaction]:
        return next((t for t in self.items if t.id == id), None)

    def add(self, tx: Transaction) -> None:
        self.items.append(tx)

    def remove(self, id: str) -> bool:
        before = len(self.items)
        self.items = [t for t in self.items if t.id != id]
        return len(self.items) != before

    def replace_all(self, items: Iterable[Transaction]) -> None:
        self.items = list(items)


def test_balance_e_report():
    svc = FinanceService(MemRepo())
    svc.add_transaction(type="income", amount=1000, description="salário", category="Trabalho")
    svc.add_transaction(type="expense", amount=200, description="mercado", category="Alimentação")
    svc.add_transaction(type="expense", amount=100, description="transporte", category="Transporte")
    assert svc.balance().amount == Money(700).amount

    r = svc.report(group_by="category")
    assert r["Trabalho"].amount == Money(1000).amount
    assert r["Alimentação"].amount == Money(-200).amount
    assert r["Transporte"].amount == Money(-100).amount
