"""
Serviço para gerenciar investimentos.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional
from .investment_models import Investment
from .investment_repository import IInvestmentRepository
from .models import Money


class InvestmentService:
    """Serviço para gerenciar investimentos do usuário."""
    
    def __init__(self, repo: IInvestmentRepository):
        self.repo = repo
    
    def create_investment(
        self,
        *,
        name: str,
        type: str,
        initial_amount: float | str,
        monthly_rate: float,
        user_id: str,
        current_amount: float | str | None = None,
        start_date: datetime | None = None,
        notes: str = ""
    ) -> Investment:
        """
        Cria um novo investimento.
        
        Args:
            name: Nome do investimento
            type: Tipo do investimento
            initial_amount: Valor inicial investido
            monthly_rate: Taxa de rendimento mensal (decimal)
            user_id: ID do usuário proprietário
            current_amount: Valor atual (opcional, padrão = initial_amount)
            start_date: Data de início (opcional, padrão = agora)
            notes: Observações adicionais
        
        Returns:
            Investment: Investimento criado
        """
        initial = Money(initial_amount)
        current = Money(current_amount) if current_amount is not None else initial
        
        investment = Investment(
            name=name.strip(),
            type=type,
            initial_amount=initial,
            current_amount=current,
            monthly_rate=monthly_rate,
            user_id=user_id,
            start_date=start_date or datetime.now(timezone.utc),
            notes=notes.strip()
        )
        
        self.repo.add(investment)
        return investment
    
    def get_investment(self, investment_id: str) -> Optional[Investment]:
        """Busca um investimento por ID."""
        return self.repo.by_id(investment_id)
    
    def list_user_investments(self, user_id: str) -> List[Investment]:
        """Lista todos os investimentos de um usuário."""
        return sorted(
            self.repo.list_by_user(user_id),
            key=lambda inv: inv.start_date,
            reverse=True
        )
    
    def update_investment(
        self,
        investment_id: str,
        *,
        name: str | None = None,
        current_amount: float | str | None = None,
        monthly_rate: float | None = None,
        notes: str | None = None
    ) -> Optional[Investment]:
        """
        Atualiza um investimento existente.
        
        Args:
            investment_id: ID do investimento
            name: Novo nome (opcional)
            current_amount: Novo valor atual (opcional)
            monthly_rate: Nova taxa mensal (opcional)
            notes: Novas observações (opcional)
        
        Returns:
            Investment: Investimento atualizado ou None se não encontrado
        """
        investment = self.repo.by_id(investment_id)
        if not investment:
            return None
        
        # Atualizar campos fornecidos
        if name is not None:
            investment = Investment(
                id=investment.id,
                name=name.strip(),
                type=investment.type,
                initial_amount=investment.initial_amount,
                current_amount=investment.current_amount,
                monthly_rate=investment.monthly_rate,
                user_id=investment.user_id,
                start_date=investment.start_date,
                notes=investment.notes
            )
        
        if current_amount is not None:
            investment = Investment(
                id=investment.id,
                name=investment.name,
                type=investment.type,
                initial_amount=investment.initial_amount,
                current_amount=Money(current_amount),
                monthly_rate=investment.monthly_rate,
                user_id=investment.user_id,
                start_date=investment.start_date,
                notes=investment.notes
            )
        
        if monthly_rate is not None:
            investment = Investment(
                id=investment.id,
                name=investment.name,
                type=investment.type,
                initial_amount=investment.initial_amount,
                current_amount=investment.current_amount,
                monthly_rate=monthly_rate,
                user_id=investment.user_id,
                start_date=investment.start_date,
                notes=investment.notes
            )
        
        if notes is not None:
            investment = Investment(
                id=investment.id,
                name=investment.name,
                type=investment.type,
                initial_amount=investment.initial_amount,
                current_amount=investment.current_amount,
                monthly_rate=investment.monthly_rate,
                user_id=investment.user_id,
                start_date=investment.start_date,
                notes=notes.strip()
            )
        
        self.repo.update(investment)
        return investment
    
    def delete_investment(self, investment_id: str) -> bool:
        """Remove um investimento."""
        return self.repo.remove(investment_id)
    
    def total_invested(self, user_id: str) -> Money:
        """Calcula o total investido pelo usuário."""
        investments = self.repo.list_by_user(user_id)
        total = Money(0)
        for inv in investments:
            total = total + inv.initial_amount
        return total
    
    def total_current_value(self, user_id: str) -> Money:
        """Calcula o valor atual total dos investimentos."""
        investments = self.repo.list_by_user(user_id)
        total = Money(0)
        for inv in investments:
            total = total + inv.current_amount
        return total
    
    def total_profit(self, user_id: str) -> Money:
        """Calcula o lucro total dos investimentos."""
        return self.total_current_value(user_id) - self.total_invested(user_id)

