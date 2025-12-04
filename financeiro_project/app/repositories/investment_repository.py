from .base import BaseRepository
from ..models import Investment

class InvestmentRepository(BaseRepository):

    def __init__(self, storage):
        self.storage = storage

    def add(self, investment):
        if not isinstance(investment, Investment):
            raise TypeError("Argumento deve ser uma instância de Investment")

        data = self.storage.load()

        if investment.user_id not in data:
            data[investment.user_id] = []

        data[investment.user_id].append(investment.to_dict())
        self.storage.save(data)

    def update(self, investment):
        if not isinstance(investment, Investment):
            raise TypeError("Argumento deve ser uma instância de Investment")

        data = self.storage.load()

        if investment.user_id not in data:
            raise ValueError(f"Nenhum investimento encontrado para o usuário '{investment.user_id}'")

        found = False
        for i, inv_data in enumerate(data[investment.user_id]):
            if inv_data['id'] == investment.id:
                data[investment.user_id][i] = investment.to_dict()
                found = True
                break

        if not found:
            raise ValueError(f"Investimento com ID '{investment.id}' não encontrado")

        self.storage.save(data)

    def delete(self, investment_id, user_id):
        data = self.storage.load()

        if user_id not in data:
            raise ValueError(f"Nenhum investimento encontrado para o usuário '{user_id}'")

        found = False
        for i, inv_data in enumerate(data[user_id]):
            if inv_data['id'] == investment_id:
                del data[user_id][i]
                found = True
                break

        if not found:
            raise ValueError(f"Investimento com ID '{investment_id}' não encontrado")

        self.storage.save(data)

    def get_by_id(self, investment_id, user_id):
        data = self.storage.load()

        if user_id not in data:
            return None

        for inv_data in data[user_id]:
            if inv_data['id'] == investment_id:
                return Investment.from_dict(inv_data)

        return None

    def list_all(self):
        data = self.storage.load()
        investments = []

        for user_id, user_investments in data.items():
            for inv_data in user_investments:
                investments.append(Investment.from_dict(inv_data))

        return investments

    def list_by_user(self, user_id):
        data = self.storage.load()

        if user_id not in data:
            return []

        return [Investment.from_dict(inv_data) for inv_data in data[user_id]]

    def list_by_user_and_type(self, user_id, type_):
        investments = self.list_by_user(user_id)
        return [inv for inv in investments if inv.type == type_]
