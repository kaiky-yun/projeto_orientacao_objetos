"""
Modelos para gerenciamento de ativos (ações e criptomoedas personalizadas)
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict
import uuid


@dataclass
class CustomAsset:
    """Representa um ativo personalizado (ação ou criptomoeda)"""
    id: str
    symbol: str  # Ex: AAPL, BTC-USD, PETR4.SA
    name: str  # Ex: Apple Inc., Bitcoin, Petrobras
    type: str  # 'stock' ou 'crypto'
    price: float  # Preço em BRL
    currency: str = 'BRL'
    created_at: str = None
    updated_at: str = None
    user_id: str = None  # Para multi-usuário
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CustomAsset':
        """Cria instância a partir de dicionário"""
        return cls(**data)
    
    @classmethod
    def create(cls, symbol: str, name: str, type: str, price: float, user_id: str = None) -> 'CustomAsset':
        """Cria novo ativo personalizado"""
        return cls(
            id=str(uuid.uuid4()),
            symbol=symbol.upper(),
            name=name,
            type=type,
            price=float(price),
            user_id=user_id
        )
    
    def update_price(self, new_price: float):
        """Atualiza o preço do ativo"""
        self.price = float(new_price)
        self.updated_at = datetime.now().isoformat()

