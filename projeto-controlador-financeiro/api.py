"""
API REST em Flask para o Controlador Financeiro.
Expõe as funcionalidades do FinanceService através de endpoints HTTP.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import os

from finance.models import Transaction, Money, Category
from finance.repository import JSONTransactionRepository
from finance.services import FinanceService
from finance.storage import JSONStorage


def create_app():
    """Factory function para criar e configurar a aplicação Flask."""
    app = Flask(__name__)
    CORS(app)  # Habilitar CORS para requisições do frontend
    
    # Inicializar o repositório e serviço
    # CORREÇÃO AQUI: Ajuste no escape da string para evitar SyntaxError
    storage_path = os.getenv('FINANCE_DB_PATH', os.path.expanduser('~/.finance_app/transactions.json'))
    storage = JSONStorage(storage_path)
    repository = JSONTransactionRepository(storage)
    service = FinanceService(repository)
    
    # ==================== FUNÇÕES AUXILIARES ====================
    
    def parse_date(date_str, end_of_day=False):
        """Parsear string de data no formato YYYY-MM-DD e retornar datetime com fuso horário UTC.
        Se end_of_day for True, define a hora para 23:59:59.
        """
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str)
            # Se a data não tiver fuso horário, assume UTC
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            return dt
        except ValueError:
            return None
    
    def filter_transactions_by_date(transactions, start_date=None, end_date=None):
        """Filtrar transações por período de tempo.
        Compara datas garantindo que ambas são timezone-aware (UTC).
        """
        if not start_date and not end_date:
            return transactions
        
        filtered = []
        for tx in transactions:
            # Garantir que tx.occurred_at é timezone-aware (UTC)
            tx_date = tx.occurred_at
            if tx_date.tzinfo is None or tx_date.tzinfo.utcoffset(tx_date) is None:
                tx_date = tx_date.replace(tzinfo=timezone.utc)
            
            if start_date and tx_date < start_date:
                continue
            if end_date and tx_date > end_date:
                continue
            
            filtered.append(tx)
        
        return filtered
    
    # ==================== ENDPOINTS ====================
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Verificar saúde da API."""
        return jsonify({'status': 'ok', 'message': 'API do Controlador Financeiro está funcionando'}), 200
    
    @app.route('/api/transactions', methods=['GET'])
    def list_transactions():
        """
        Listar transações ordenadas por data.
        Query params opcionais:
        - start_date: Data inicial (YYYY-MM-DD)
        - end_date: Data final (YYYY-MM-DD)
        """
        try:
            transactions = service.list_transactions()
            
            # Aplicar filtro de data se fornecido
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')
            
            start_dt = parse_date(start_date_str)
            end_dt = parse_date(end_date_str, end_of_day=True)
            
            transactions = filter_transactions_by_date(transactions, start_dt, end_dt)
            
            return jsonify({
                'success': True,
                'data': [tx.to_dict() for tx in transactions]
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/transactions', methods=['POST'])
    def create_transaction():
        """Criar uma nova transação."""
        try:
            data = request.get_json()
            
            # Validar campos obrigatórios
            required_fields = ['type', 'amount', 'description', 'category']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': f'Campos obrigatórios: {", ".join(required_fields)}'
                }), 400
            
            # Validar tipo de transação
            if data['type'] not in ['income', 'expense']:
                return jsonify({
                    'success': False,
                    'error': 'Tipo deve ser "income" ou "expense"'
                }), 400
            
            # Criar transação
            occurred_at = None
            if 'occurred_at' in data and data['occurred_at']:
                try:
                    # Garante que a data salva é timezone-aware (UTC)
                    dt_naive = datetime.fromisoformat(data['occurred_at'])
                    occurred_at = dt_naive.replace(tzinfo=timezone.utc)
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Data inválida. Use formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)'
                    }), 400
            
            transaction = service.add_transaction(
                type=data['type'],
                amount=data['amount'],
                description=data['description'],
                category=data['category'],
                occurred_at=occurred_at
            )
            
            return jsonify({
                'success': True,
                'data': transaction.to_dict()
            }), 201
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/transactions/<transaction_id>', methods=['GET'])
    def get_transaction(transaction_id):
        """Obter uma transação específica pelo ID."""
        try:
            transaction = repository.by_id(transaction_id)
            if not transaction:
                return jsonify({
                    'success': False,
                    'error': 'Transação não encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'data': transaction.to_dict()
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
    def delete_transaction(transaction_id):
        """Deletar uma transação pelo ID."""
        try:
            removed = service.remove(transaction_id)
            if not removed:
                return jsonify({
                    'success': False,
                    'error': 'Transação não encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Transação removida com sucesso'
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/balance', methods=['GET'])
    def get_balance():
        """
        Obter o saldo total (receitas - despesas).
        Query params opcionais:
        - start_date: Data inicial (YYYY-MM-DD)
        - end_date: Data final (YYYY-MM-DD)
        """
        try:
            transactions = service.list_transactions()
            
            # Aplicar filtro de data se fornecido
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')
            
            start_dt = parse_date(start_date_str)
            end_dt = parse_date(end_date_str, end_of_day=True)
            
            transactions = filter_transactions_by_date(transactions, start_dt, end_dt)
            
            # Calcular saldo
            balance = Money(0)
            for tx in transactions:
                balance = balance + tx.signed_amount
            
            return jsonify({
                'success': True,
                'data': {
                    'balance': str(balance.amount),
                    'currency': 'BRL'
                }
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/report', methods=['GET'])
    def get_report():
        """
        Gerar relatório agrupado por categoria ou mês.
        Query params:
        - group_by: 'category' ou 'month' (default: 'category')
        - start_date: Data inicial (YYYY-MM-DD) - opcional
        - end_date: Data final (YYYY-MM-DD) - opcional
        """
        try:
            group_by = request.args.get('group_by', 'category')
            
            if group_by not in ['category', 'month']:
                return jsonify({
                    'success': False,
                    'error': 'group_by deve ser "category" ou "month"'
                }), 400
            
            # Obter transações
            transactions = service.list_transactions()
            
            # Aplicar filtro de data se fornecido
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')
            
            start_dt = parse_date(start_date_str)
            end_dt = parse_date(end_date_str, end_of_day=True)
            
            transactions = filter_transactions_by_date(transactions, start_dt, end_dt)
            
            # Gerar relatório
            from collections import defaultdict
            groups = defaultdict(lambda: Money(0))
            
            for tx in transactions:
                if group_by == 'category':
                    key = tx.category.name
                else:  # month
                    # Garante que a data é timezone-aware antes de formatar
                    tx_date_aware = tx.occurred_at
                    if tx_date_aware.tzinfo is None or tx_date_aware.tzinfo.utcoffset(tx_date_aware) is None:
                        tx_date_aware = tx_date_aware.replace(tzinfo=timezone.utc)
                    key = tx_date_aware.strftime("%Y-%m")
                
                groups[key] = groups[key] + tx.signed_amount
            
            # Converter Money para string para serialização JSON
            report_data = {key: str(value.amount) for key, value in groups.items()}
            
            return jsonify({
                'success': True,
                'data': report_data,
                'group_by': group_by
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        """Obter lista de categorias únicas usadas nas transações."""
        try:
            transactions = service.list_transactions()
            categories = sorted(set(tx.category.name for tx in transactions))
            return jsonify({
                'success': True,
                'data': categories
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ERROR HANDLERS ====================
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint não encontrado'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5010)
