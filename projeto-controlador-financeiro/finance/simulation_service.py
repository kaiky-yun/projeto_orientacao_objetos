"""
Serviço para simulação de investimentos.
Baseado nas planilhas de simulação fornecidas.
"""

from __future__ import annotations
from typing import List, Dict
from dataclasses import dataclass
from decimal import Decimal
from .models import Money


@dataclass
class MonthlyProjection:
    """Representa a projeção de um mês específico."""
    month: int
    contribution: Money
    accumulated_balance: Money
    profit: Money


@dataclass
class SimulationResult:
    """Resultado completo de uma simulação."""
    initial_amount: Money
    monthly_rate: float
    total_months: int
    projections: List[MonthlyProjection]
    total_contributed: Money
    final_balance: Money
    total_profit: Money
    
    def to_dict(self) -> dict:
        """Serializa resultado da simulação."""
        return {
            "initial_amount": str(self.initial_amount.amount),
            "monthly_rate": self.monthly_rate,
            "total_months": self.total_months,
            "projections": [
                {
                    "month": p.month,
                    "contribution": str(p.contribution.amount),
                    "accumulated_balance": str(p.accumulated_balance.amount),
                    "profit": str(p.profit.amount)
                }
                for p in self.projections
            ],
            "total_contributed": str(self.total_contributed.amount),
            "final_balance": str(self.final_balance.amount),
            "total_profit": str(self.total_profit.amount)
        }


class SimulationService:
    """Serviço para simular investimentos."""
    
    @staticmethod
    def simulate_fixed_contribution(
        initial_amount: float | str,
        monthly_contribution: float | str,
        monthly_rate: float,
        months: int
    ) -> SimulationResult:
        """
        Simula investimento com aporte mensal fixo.
        
        Baseado na lógica das planilhas:
        - Saldo[n] = Saldo[n-1] * (1 + taxa) + Aporte[n]
        
        Args:
            initial_amount: Valor inicial investido
            monthly_contribution: Aporte mensal fixo
            monthly_rate: Taxa de rendimento mensal (decimal, ex: 0.008 = 0.8%)
            months: Número de meses a simular
        
        Returns:
            SimulationResult: Resultado completo da simulação
        """
        initial = Money(initial_amount)
        contribution = Money(monthly_contribution)
        
        projections: List[MonthlyProjection] = []
        current_balance = initial
        total_contributed = initial
        
        # Mês 0 (inicial)
        projections.append(MonthlyProjection(
            month=0,
            contribution=initial,
            accumulated_balance=current_balance,
            profit=Money(0)
        ))
        
        # Simular meses seguintes
        for month in range(1, months + 1):
            # Aplicar rendimento
            interest = current_balance * Decimal(str(monthly_rate))
            current_balance = current_balance + Money(interest.amount)
            
            # Adicionar aporte
            current_balance = current_balance + contribution
            total_contributed = total_contributed + contribution
            
            # Calcular lucro acumulado
            profit = current_balance - total_contributed
            
            projections.append(MonthlyProjection(
                month=month,
                contribution=contribution,
                accumulated_balance=current_balance,
                profit=profit
            ))
        
        return SimulationResult(
            initial_amount=initial,
            monthly_rate=monthly_rate,
            total_months=months,
            projections=projections,
            total_contributed=total_contributed,
            final_balance=current_balance,
            total_profit=current_balance - total_contributed
        )
    
    @staticmethod
    def simulate_variable_contribution(
        initial_amount: float | str,
        monthly_contributions: List[float | str],
        monthly_rate: float
    ) -> SimulationResult:
        """
        Simula investimento com aportes mensais variáveis.
        
        Baseado na planilha "Simulacao_Aportes_Variaveis_Interativo.xlsx".
        
        Args:
            initial_amount: Valor inicial investido
            monthly_contributions: Lista de aportes mensais (um por mês)
            monthly_rate: Taxa de rendimento mensal (decimal)
        
        Returns:
            SimulationResult: Resultado completo da simulação
        """
        initial = Money(initial_amount)
        
        projections: List[MonthlyProjection] = []
        current_balance = initial
        total_contributed = initial
        
        # Mês 0 (inicial)
        projections.append(MonthlyProjection(
            month=0,
            contribution=initial,
            accumulated_balance=current_balance,
            profit=Money(0)
        ))
        
        # Simular cada mês com aporte variável
        for month, contribution_value in enumerate(monthly_contributions, start=1):
            contribution = Money(contribution_value)
            
            # Aplicar rendimento
            interest = current_balance * Decimal(str(monthly_rate))
            current_balance = current_balance + Money(interest.amount)
            
            # Adicionar aporte
            current_balance = current_balance + contribution
            total_contributed = total_contributed + contribution
            
            # Calcular lucro acumulado
            profit = current_balance - total_contributed
            
            projections.append(MonthlyProjection(
                month=month,
                contribution=contribution,
                accumulated_balance=current_balance,
                profit=profit
            ))
        
        return SimulationResult(
            initial_amount=initial,
            monthly_rate=monthly_rate,
            total_months=len(monthly_contributions),
            projections=projections,
            total_contributed=total_contributed,
            final_balance=current_balance,
            total_profit=current_balance - total_contributed
        )
    
    @staticmethod
    def compare_scenarios(
        initial_amount: float | str,
        monthly_contributions: List[float | str],
        monthly_rate: float,
        months: int
    ) -> Dict[str, SimulationResult]:
        """
        Compara múltiplos cenários de investimento.
        
        Baseado na planilha "Simulacao_Investimentos_Kaiky.xlsx" que tem
        abas com diferentes valores de aporte (R$1000, R$1500, R$2000).
        
        Args:
            initial_amount: Valor inicial
            monthly_contributions: Lista de valores de aporte mensal para comparar
            monthly_rate: Taxa mensal
            months: Número de meses
        
        Returns:
            Dicionário com resultados de cada cenário
        """
        scenarios = {}
        
        for contribution in monthly_contributions:
            key = f"aporte_{Money(contribution).amount}"
            scenarios[key] = SimulationService.simulate_fixed_contribution(
                initial_amount=initial_amount,
                monthly_contribution=contribution,
                monthly_rate=monthly_rate,
                months=months
            )
        
        return scenarios

