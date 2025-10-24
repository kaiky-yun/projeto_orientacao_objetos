"""
Repositório para gerenciar investimentos.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from .investment_models import Investment
from .storage import JSONStorage


class IInvestmentRepository(ABC):
    """Interface para repositório de investimentos."""
    
    @abstractmethod
    def add(self, investment: Investment) -> None:
        """Adiciona um novo investimento."""
        pass
    
    @abstractmethod
    def by_id(self, investment_id: str) -> Optional[Investment]:
        """Busca investimento por ID."""
        pass
    
    @abstractmethod
    def list(self) -> List[Investment]:
        """Lista todos os investimentos."""
        pass
    
    @abstractmethod
    def list_by_user(self, user_id: str) -> List[Investment]:
        """Lista investimentos de um usuário específico."""
        pass
    
    @abstractmethod
    def update(self, investment: Investment) -> bool:
        """Atualiza um investimento existente."""
        pass
    
    @abstractmethod
    def remove(self, investment_id: str) -> bool:
        """Remove um investimento pelo ID."""
        pass


class JSONInvestmentRepository(IInvestmentRepository):
    """Implementação de repositório de investimentos usando JSONStorage."""
    
    def __init__(self, storage: JSONStorage):
        self.storage = storage
    
    def add(self, investment: Investment) -> None:
        """Adiciona um novo investimento."""
        data = self.storage.load()
        data.append(investment.to_dict())
        self.storage.save(data)
    
    def by_id(self, investment_id: str) -> Optional[Investment]:
        """Busca investimento por ID."""
        data = self.storage.load()
        for item in data:
            if item["id"] == investment_id:
                return Investment.from_dict(item)
        return None
    
    def list(self) -> List[Investment]:
        """Lista todos os investimentos."""
        data = self.storage.load()
        return [Investment.from_dict(item) for item in data]
    
    def list_by_user(self, user_id: str) -> List[Investment]:
        """Lista investimentos de um usuário específico."""
        all_investments = self.list()
        return [inv for inv in all_investments if inv.user_id == user_id]
    
    def update(self, investment: Investment) -> bool:
        """Atualiza um investimento existente."""
        data = self.storage.load()
        for i, item in enumerate(data):
            if item["id"] == investment.id:
                data[i] = investment.to_dict()
                self.storage.save(data)
                return True
        return False
    
    def remove(self, investment_id: str) -> bool:
        """Remove um investimento pelo ID."""
        data = self.storage.load()
        original_len = len(data)
        data = [item for item in data if item["id"] != investment_id]
        if len(data) < original_len:
            self.storage.save(data)
            return True
        return False

