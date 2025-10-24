"""
Repositório para gerenciamento de ativos personalizados
"""
from typing import List, Optional
from .asset_models import CustomAsset
from .storage import JSONStorage


class AssetRepository:
    """Repositório para operações CRUD de ativos personalizados"""
    
    def __init__(self, storage_path: str = '~/.finance_app/custom_assets.json'):
        self.storage = JSONStorage(storage_path)
    
    def add(self, asset: CustomAsset) -> CustomAsset:
        """Adiciona novo ativo"""
        assets = self.storage.load()
        assets.append(asset.to_dict())
        self.storage.save(assets)
        return asset
    
    def get_all(self, user_id: str = None) -> List[CustomAsset]:
        """Retorna todos os ativos (opcionalmente filtrados por usuário)"""
        assets = self.storage.load()
        
        if user_id:
            assets = [a for a in assets if a.get('user_id') == user_id]
        
        return [CustomAsset.from_dict(a) for a in assets]
    
    def get_by_id(self, asset_id: str) -> Optional[CustomAsset]:
        """Busca ativo por ID"""
        assets = self.storage.load()
        
        for asset_data in assets:
            if asset_data['id'] == asset_id:
                return CustomAsset.from_dict(asset_data)
        
        return None
    
    def get_by_symbol(self, symbol: str, user_id: str = None) -> Optional[CustomAsset]:
        """Busca ativo por símbolo"""
        assets = self.storage.load()
        symbol = symbol.upper()
        
        for asset_data in assets:
            if asset_data['symbol'] == symbol:
                if user_id is None or asset_data.get('user_id') == user_id:
                    return CustomAsset.from_dict(asset_data)
        
        return None
    
    def update(self, asset: CustomAsset) -> CustomAsset:
        """Atualiza ativo existente"""
        assets = self.storage.load()
        
        for i, asset_data in enumerate(assets):
            if asset_data['id'] == asset.id:
                assets[i] = asset.to_dict()
                self.storage.save(assets)
                return asset
        
        raise ValueError(f"Ativo com ID {asset.id} não encontrado")
    
    def delete(self, asset_id: str) -> bool:
        """Remove ativo"""
        assets = self.storage.load()
        original_length = len(assets)
        
        assets = [a for a in assets if a['id'] != asset_id]
        
        if len(assets) < original_length:
            self.storage.save(assets)
            return True
        
        return False
    
    def search(self, query: str, user_id: str = None) -> List[CustomAsset]:
        """Busca ativos por nome ou símbolo"""
        assets = self.get_all(user_id)
        query = query.lower()
        
        return [
            asset for asset in assets
            if query in asset.name.lower() or query in asset.symbol.lower()
        ]

