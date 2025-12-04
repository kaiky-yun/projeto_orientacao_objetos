from datetime import datetime, timezone
from .base import BaseRepository
from ..models import Transaction

class TransactionRepository(BaseRepository):

    def __init__(self, storage):
        self.storage = storage

    def add(self, transaction):
        if not isinstance(transaction, Transaction):
            raise TypeError("Argumento deve ser uma instância de Transaction")

        data = self.storage.load()

        if transaction.user_id not in data:
            data[transaction.user_id] = []

        data[transaction.user_id].append(transaction.to_dict())
        self.storage.save(data)

    def update(self, transaction):
        if not isinstance(transaction, Transaction):
            raise TypeError("Argumento deve ser uma instância de Transaction")

        data = self.storage.load()

        if transaction.user_id not in data:
            raise ValueError(f"Nenhuma transação encontrada para o usuário '{transaction.user_id}'")

        found = False
        for i, tx_data in enumerate(data[transaction.user_id]):
            if tx_data['id'] == transaction.id:
                data[transaction.user_id][i] = transaction.to_dict()
                found = True
                break

        if not found:
            raise ValueError(f"Transação com ID '{transaction.id}' não encontrada")

        self.storage.save(data)

    def delete(self, transaction_id, user_id):
        data = self.storage.load()

        if user_id not in data:
            raise ValueError(f"Nenhuma transação encontrada para o usuário '{user_id}'")

        found = False
        for i, tx_data in enumerate(data[user_id]):
            if tx_data['id'] == transaction_id:
                del data[user_id][i]
                found = True
                break

        if not found:
            raise ValueError(f"Transação com ID '{transaction_id}' não encontrada")

        self.storage.save(data)

    def get_by_id(self, transaction_id, user_id):
        data = self.storage.load()

        if user_id not in data:
            return None

        for tx_data in data[user_id]:
            if tx_data['id'] == transaction_id:
                return Transaction.from_dict(tx_data)

        return None

    def list_all(self):
        data = self.storage.load()
        transactions = []

        for user_id, user_transactions in data.items():
            for tx_data in user_transactions:
                transactions.append(Transaction.from_dict(tx_data))

        return transactions

    def list_by_user(self, user_id):
        data = self.storage.load()

        if user_id not in data:
            return []

        return [Transaction.from_dict(tx_data) for tx_data in data[user_id]]

    def list_by_user_and_type(self, user_id, type_):
        transactions = self.list_by_user(user_id)
        return [tx for tx in transactions if tx.type == type_]

    def list_by_user_and_date_range(self, user_id, start_date=None, end_date=None):
        transactions = self.list_by_user(user_id)

        if not start_date and not end_date:
            return transactions

        filtered = []
        for tx in transactions:
            tx_date = tx.occurred_at

            if tx_date.tzinfo is None:
                tx_date = tx_date.replace(tzinfo=timezone.utc)

            if start_date and tx_date < start_date:
                continue

            if end_date and tx_date > end_date:
                continue

            filtered.append(tx)

        return filtered
