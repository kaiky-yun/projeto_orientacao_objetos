from ..models import Investment, Money

class InvestmentService:

    def __init__(self, investment_repository):
        self.investment_repository = investment_repository

    def create_investment(self, name, type_, initial_amount, current_amount, monthly_rate, user_id, start_date=None, notes=''):
        investment = Investment(
            name=name,
            type_=type_,
            initial_amount=initial_amount,
            current_amount=current_amount,
            monthly_rate=monthly_rate,
            user_id=user_id,
            start_date=start_date,
            notes=notes
        )

        self.investment_repository.add(investment)
        return investment

    def update_investment(self, investment_id, user_id, **kwargs):

        investment = self.investment_repository.get_by_id(investment_id, user_id)

        if not investment:
            raise ValueError(f"Investimento com ID '{investment_id}' não encontrado")

        name = kwargs.get('name', investment.name)
        type_ = kwargs.get('type', investment.type)
        initial_amount = kwargs.get('initial_amount', investment.initial_amount)
        current_amount = kwargs.get('current_amount', investment.current_amount)
        monthly_rate = kwargs.get('monthly_rate', investment.monthly_rate)
        start_date = kwargs.get('start_date', investment.start_date)
        notes = kwargs.get('notes', investment.notes)

        updated_investment = Investment(
            name=name,
            type_=type_,
            initial_amount=initial_amount,
            current_amount=current_amount,
            monthly_rate=monthly_rate,
            user_id=user_id,
            start_date=start_date,
            notes=notes,
            id_=investment_id
        )

        self.investment_repository.update(updated_investment)
        return updated_investment

    def delete_investment(self, investment_id, user_id):
        self.investment_repository.delete(investment_id, user_id)

    def get_investment(self, investment_id, user_id):
        return self.investment_repository.get_by_id(investment_id, user_id)

    def list_investments(self, user_id):
        return self.investment_repository.list_by_user(user_id)

    def list_investments_by_type(self, user_id, type_):
        return self.investment_repository.list_by_user_and_type(user_id, type_)

    def get_total_invested(self, user_id):
        investments = self.list_investments(user_id)

        total = Money(0)
        for inv in investments:
            total = total + inv.initial_amount

        return total

    def get_total_current_value(self, user_id):
        investments = self.list_investments(user_id)

        total = Money(0)
        for inv in investments:
            total = total + inv.current_amount

        return total

    def get_total_profit(self, user_id):
        investments = self.list_investments(user_id)

        total = Money(0)
        for inv in investments:
            total = total + inv.profit

        return total
