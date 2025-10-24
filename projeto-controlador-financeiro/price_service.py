"""
Serviço para buscar cotações de ações e criptomoedas em tempo real.
"""

import sys
sys.path.append('/opt/.manus/.sandbox-runtime')

from typing import Optional, Dict
from decimal import Decimal
from datetime import datetime


class PriceService:
    """Serviço para buscar preços de ativos financeiros."""
    
    def __init__(self):
        """Inicializa o serviço de preços."""
        try:
            from data_api import ApiClient
            self.client = ApiClient()
            self.api_available = True
        except ImportError:
            # API Client não disponível - usar preços simulados silenciosamente
            self.api_available = False
    
    def get_stock_price(self, symbol: str, region: str = "US") -> Optional[Dict]:
        """
        Busca o preço atual de uma ação.
        
        Args:
            symbol: Símbolo da ação (ex: AAPL, PETR4.SA)
            region: Região do mercado (US, BR, etc)
        
        Returns:
            Dict com informações do preço ou None se não encontrado
        """
        if not self.api_available:
            return self._get_mock_stock_price(symbol)
        
        try:
            response = self.client.call_api('YahooFinance/get_stock_chart', query={
                'symbol': symbol,
                'region': region,
                'interval': '1d',
                'range': '1d',
                'includeAdjustedClose': True
            })
            
            if response and 'chart' in response and 'result' in response['chart']:
                result = response['chart']['result'][0]
                meta = result['meta']
                
                return {
                    'symbol': meta['symbol'],
                    'name': meta.get('longName', meta.get('shortName', symbol)),
                    'price': Decimal(str(meta['regularMarketPrice'])),
                    'currency': meta['currency'],
                    'exchange': meta['exchangeName'],
                    'timestamp': datetime.now().isoformat(),
                    'day_high': Decimal(str(meta.get('regularMarketDayHigh', 0))),
                    'day_low': Decimal(str(meta.get('regularMarketDayLow', 0))),
                    'volume': meta.get('regularMarketVolume', 0),
                    'source': 'Yahoo Finance'
                }
        except Exception as e:
            print(f"Erro ao buscar preço de {symbol}: {e}")
            return None
        
        return None
    
    def get_crypto_price(self, symbol: str) -> Optional[Dict]:
        """
        Busca o preço atual de uma criptomoeda.
        
        Args:
            symbol: Símbolo da cripto (ex: BTC-USD, ETH-USD)
        
        Returns:
            Dict com informações do preço ou None se não encontrado
        """
        # Criptomoedas também podem ser buscadas via Yahoo Finance
        # Adicionar -USD se não tiver sufixo
        if '-' not in symbol:
            symbol = f"{symbol}-USD"
        
        return self.get_stock_price(symbol, region="US")
    
    def _get_mock_stock_price(self, symbol: str) -> Dict:
        """Retorna preços simulados para desenvolvimento (TODOS EM BRL)."""
        # Taxa de câmbio USD para BRL (atualizada 24/10/2025)
        USD_TO_BRL = 5.65
        
        mock_prices = {
            # Ações US (convertidas para BRL - preços de 24/10/2025)
            'AAPL': {'name': 'Apple Inc.', 'price': 1467.12},  # $259.58 * 5.65
            'GOOGL': {'name': 'Alphabet Inc.', 'price': 960.00},  # ~$170 * 5.65
            'MSFT': {'name': 'Microsoft Corporation', 'price': 2962.30},  # $524.30 * 5.65
            'TSLA': {'name': 'Tesla Inc.', 'price': 1525.00},  # ~$270 * 5.65
            'AMZN': {'name': 'Amazon.com Inc.', 'price': 1130.00},  # ~$200 * 5.65
            
            # Ações BR (preços de 24/10/2025)
            'PETR4.SA': {'name': 'Petrobras PN', 'price': 30.26},
            'VALE3.SA': {'name': 'Vale ON', 'price': 58.50},
            'ITUB4.SA': {'name': 'Itaú Unibanco PN', 'price': 26.80},
            'BBDC4.SA': {'name': 'Bradesco PN', 'price': 13.50},
            'ABEV3.SA': {'name': 'Ambev ON', 'price': 11.90},
            
            # Criptomoedas (convertidas para BRL - preços de 24/10/2025)
            'BTC-USD': {'name': 'Bitcoin', 'price': 625829.50},  # $110,554.80 * 5.65
            'ETH-USD': {'name': 'Ethereum', 'price': 22038.05},  # $3,902.17 * 5.65
            'BNB-USD': {'name': 'Binance Coin', 'price': 6216.53},  # $1,100.27 * 5.65
            'ADA-USD': {'name': 'Cardano', 'price': 2.26},  # ~$0.40 * 5.65
            'SOL-USD': {'name': 'Solana', 'price': 1017.00},  # ~$180 * 5.65
        }
        
        data = mock_prices.get(symbol, {'name': symbol, 'price': 100.00})
        
        return {
            'symbol': symbol,
            'name': data['name'],
            'price': Decimal(str(data['price'])),
            'currency': 'BRL',  # SEMPRE BRL
            'exchange': 'B3' if '.SA' in symbol else 'NASDAQ',
            'timestamp': datetime.now().isoformat(),
            'day_high': Decimal(str(data['price'] * 1.02)),
            'day_low': Decimal(str(data['price'] * 0.98)),
            'volume': 1000000,
            'source': 'Dados Simulados (em BRL)'
        }
    
    def search_symbol(self, query: str) -> list:
        """
        Busca símbolos de ações/criptos baseado em uma query.
        
        Args:
            query: Texto para buscar (nome da empresa ou símbolo)
        
        Returns:
            Lista de símbolos encontrados
        """
        # Símbolos comuns para sugestão
        common_symbols = {
            # Ações US
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'nvidia': 'NVDA',
            
            # Ações BR
            'petrobras': 'PETR4.SA',
            'vale': 'VALE3.SA',
            'itau': 'ITUB4.SA',
            'bradesco': 'BBDC4.SA',
            'ambev': 'ABEV3.SA',
            'magazine luiza': 'MGLU3.SA',
            
            # Criptomoedas
            'bitcoin': 'BTC-USD',
            'ethereum': 'ETH-USD',
            'binance': 'BNB-USD',
            'cardano': 'ADA-USD',
            'solana': 'SOL-USD',
            'ripple': 'XRP-USD',
        }
        
        query_lower = query.lower()
        results = []
        
        for name, symbol in common_symbols.items():
            if query_lower in name or query_lower in symbol.lower():
                results.append({
                    'symbol': symbol,
                    'name': name.title()
                })
        
        return results[:10]  # Limitar a 10 resultados
    
    def _custom_asset_to_price_data(self, asset) -> Dict:
        """Converte ativo personalizado em formato de dados de preço.
        
        Args:
            asset: CustomAsset
        
        Returns:
            Dict com dados de preço formatados
        """
        return {
            'symbol': asset.symbol,
            'name': asset.name,
            'price': asset.price,
            'currency': 'BRL',
            'day_high': asset.price * 1.02,  # Simular variação de +2%
            'day_low': asset.price * 0.98,   # Simular variação de -2%
            'source': 'Ativo Personalizado',
            'timestamp': asset.updated_at,
            'custom': True
        }

