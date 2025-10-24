"""
Serviço especializado para geração de relatórios avançados.
"""

from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from .models import Transaction, Money
from .repository import ITransactionRepository


class ReportService:
    """Serviço para gerar relatórios financeiros avançados."""
    
    def __init__(self, repo: ITransactionRepository):
        self.repo = repo
    
    def monthly_by_category(
        self, 
        user_id: str, 
        year: int | None = None, 
        month: int | None = None
    ) -> Dict[str, Dict[str, Money]]:
        """
        Gera relatório mensal detalhado por categoria.
        
        Args:
            user_id: ID do usuário
            year: Ano específico (opcional)
            month: Mês específico (opcional, requer year)
        
        Returns:
            Dicionário no formato:
            {
                "2025-01": {
                    "Alimentação": Money(-500.00),
                    "Salário": Money(3000.00),
                    ...
                },
                "2025-02": {...}
            }
        """
        transactions = self.repo.list_by_user(user_id)
        
        # Estrutura: {month: {category: total}}
        report: Dict[str, Dict[str, Money]] = defaultdict(lambda: defaultdict(lambda: Money(0)))
        
        for tx in transactions:
            tx_date = tx.occurred_at
            tx_year = tx_date.year
            tx_month = tx_date.month
            
            # Filtrar por ano/mês se especificado
            if year is not None and tx_year != year:
                continue
            if month is not None and tx_month != month:
                continue
            
            month_key = f"{tx_year:04d}-{tx_month:02d}"
            category_key = tx.category.name
            
            report[month_key][category_key] = report[month_key][category_key] + tx.signed_amount
        
        # Converter defaultdict para dict normal
        return {
            month: dict(categories) 
            for month, categories in sorted(report.items())
        }
    
    def category_by_month(
        self,
        user_id: str,
        category: str,
        year: int | None = None
    ) -> Dict[str, Money]:
        """
        Gera relatório de uma categoria específica ao longo dos meses.
        
        Args:
            user_id: ID do usuário
            category: Nome da categoria
            year: Ano específico (opcional)
        
        Returns:
            Dicionário no formato:
            {
                "2025-01": Money(-500.00),
                "2025-02": Money(-450.00),
                ...
            }
        """
        transactions = self.repo.list_by_user(user_id)
        
        report: Dict[str, Money] = defaultdict(lambda: Money(0))
        
        for tx in transactions:
            if tx.category.name != category:
                continue
            
            tx_date = tx.occurred_at
            tx_year = tx_date.year
            tx_month = tx_date.month
            
            if year is not None and tx_year != year:
                continue
            
            month_key = f"{tx_year:04d}-{tx_month:02d}"
            report[month_key] = report[month_key] + tx.signed_amount
        
        return dict(sorted(report.items()))
    
    def available_months(self, user_id: str) -> List[str]:
        """
        Retorna lista de meses disponíveis (com transações).
        
        Returns:
            Lista de strings no formato "YYYY-MM"
        """
        transactions = self.repo.list_by_user(user_id)
        months = set()
        
        for tx in transactions:
            tx_date = tx.occurred_at
            month_key = f"{tx_date.year:04d}-{tx_date.month:02d}"
            months.add(month_key)
        
        return sorted(list(months))
    
    def summary_by_month(
        self,
        user_id: str,
        year: int | None = None,
        month: int | None = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Gera resumo financeiro por mês (receitas, despesas, saldo).
        
        Returns:
            Dicionário no formato:
            {
                "2025-01": {
                    "income": "5000.00",
                    "expense": "3000.00",
                    "balance": "2000.00"
                },
                ...
            }
        """
        transactions = self.repo.list_by_user(user_id)
        
        summary: Dict[str, Dict[str, Money]] = defaultdict(
            lambda: {
                "income": Money(0),
                "expense": Money(0),
                "balance": Money(0)
            }
        )
        
        for tx in transactions:
            tx_date = tx.occurred_at
            tx_year = tx_date.year
            tx_month = tx_date.month
            
            if year is not None and tx_year != year:
                continue
            if month is not None and tx_month != month:
                continue
            
            month_key = f"{tx_year:04d}-{tx_month:02d}"
            
            if tx.type == "income":
                summary[month_key]["income"] = summary[month_key]["income"] + tx.amount
            else:
                summary[month_key]["expense"] = summary[month_key]["expense"] + tx.amount
            
            summary[month_key]["balance"] = summary[month_key]["balance"] + tx.signed_amount
        
        # Converter Money para string
        result = {}
        for month, values in sorted(summary.items()):
            result[month] = {
                "income": str(values["income"].amount),
                "expense": str(values["expense"].amount),
                "balance": str(values["balance"].amount)
            }
        
        return result

