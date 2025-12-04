from datetime import datetime, timezone
from ..models import Transaction, Money, Category

class FinanceService:

    def __init__(self, transaction_repository):
        self.transaction_repository = transaction_repository

    def create_transaction(self, type_, amount, description, category, user_id, occurred_at=None):
        transaction = Transaction(
            type_=type_,
            amount=amount,
            description=description,
            category=Category(category, type_, user_id),
            user_id=user_id,
            occurred_at=occurred_at
        )

        self.transaction_repository.add(transaction)
        return transaction

    def update_transaction(self, transaction_id, user_id, **kwargs):

        transaction = self.transaction_repository.get_by_id(transaction_id, user_id)

        if not transaction:
            raise ValueError(f"Transação com ID '{transaction_id}' não encontrada")

        type_ = kwargs.get('type', transaction.type)
        amount = kwargs.get('amount', transaction.amount)
        description = kwargs.get('description', transaction.description)
        category = kwargs.get('category', transaction.category)
        occurred_at = kwargs.get('occurred_at', transaction.occurred_at)

        updated_transaction = Transaction(
            type_=type_,
            amount=amount,
            description=description,
            category=Category(category, type_, user_id),
            user_id=user_id,
            occurred_at=occurred_at,
            id_=transaction_id
        )

        self.transaction_repository.update(updated_transaction)
        return updated_transaction

    def delete_transaction(self, transaction_id, user_id):
        self.transaction_repository.delete(transaction_id, user_id)

    def get_transaction(self, transaction_id, user_id):
        return self.transaction_repository.get_by_id(transaction_id, user_id)

    def list_transactions(self, user_id):
        return self.transaction_repository.list_by_user(user_id)

    def list_transactions_by_type(self, user_id, type_):
        return self.transaction_repository.list_by_user_and_type(user_id, type_)

    def list_transactions_by_date_range(self, user_id, start_date=None, end_date=None):
        return self.transaction_repository.list_by_user_and_date_range(user_id, start_date, end_date)

    def get_balance(self, user_id):
        transactions = self.list_transactions(user_id)

        total = Money(0)
        for tx in transactions:
            total = total + tx.signed_amount

        return total

    def get_income_total(self, user_id):
        transactions = self.list_transactions_by_type(user_id, 'income')

        total = Money(0)
        for tx in transactions:
            total = total + tx.amount

        return total

    def get_expense_total(self, user_id):
        transactions = self.list_transactions_by_type(user_id, 'expense')

        total = Money(0)
        for tx in transactions:
            total = total + tx.amount

        return total

    def get_expenses_by_category(self, user_id):
        expenses = self.list_transactions_by_type(user_id, 'expense')

        by_category = {}
        for expense in expenses:
            category_name = expense.category.name
            if category_name not in by_category:
                by_category[category_name] = Money(0)
            by_category[category_name] = by_category[category_name] + expense.amount

        return by_category
