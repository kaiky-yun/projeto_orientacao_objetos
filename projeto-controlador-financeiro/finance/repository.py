from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Optional
from .models import Transaction
from .storage import JSONStorage


class ITransactionRepository(ABC):
    @abstractmethod
    def list(self) -> list[Transaction]: ...
    @abstractmethod
    def by_id(self, id: str) -> Optional[Transaction]: ...
    @abstractmethod
    def add(self, tx: Transaction) -> None: ...
    @abstractmethod
    def remove(self, id: str) -> bool: ...
    @abstractmethod
    def replace_all(self, items: Iterable[Transaction]) -> None: ...


class JSONTransactionRepository(ITransactionRepository):
    def __init__(self, storage: JSONStorage | None = None):
        self.storage = storage or JSONStorage()

    def list(self) -> list[Transaction]:
        raw = self.storage.get_all()
        return [Transaction.from_dict(d) for d in raw]

    def by_id(self, id: str) -> Optional[Transaction]:
        return next((tx for tx in self.list() if tx.id == id), None)

    def add(self, tx: Transaction) -> None:
        items = self.list()
        items.append(tx)
        self.storage.save_all([t.to_dict() for t in items])

    def remove(self, id: str) -> bool:
        items = self.list()
        after = [t for t in items if t.id != id]
        self.storage.save_all([t.to_dict() for t in after])
        return len(after) != len(items)

    def replace_all(self, items: Iterable[Transaction]) -> None:
        self.storage.save_all([t.to_dict() for t in items])
