"""
API REST em Flask para o Controlador Financeiro.
Expõe as funcionalidades do FinanceService através de endpoints HTTP.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
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
    storage_path = os.getenv('FINANCE_DB_PATH', os.path.expanduser('~/.finance_app/transactions.json'))
    storage = JSONStorage(storage_path)
    repository = JSONTransactionRepository(storage)
    service = FinanceService(repository)
    
    # ==================== ENDPOINTS ====================
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Verificar saúde da API."""
        return jsonify({'status': 'ok', 'message': 'API do Controlador Financeiro está funcionando'}), 200
    
    @app.route('/api/transactions', methods=['GET'])
    def list_transactions():
        """Listar todas as transações ordenadas por data."""
        try:
            transactions = service.list_transactions()
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
                    occurred_at = datetime.fromisoformat(data['occurred_at'])
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
        """Obter o saldo total (receitas - despesas)."""
        try:
            balance = service.balance()
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
        Query param: group_by (default: 'category', options: 'category', 'month')
        """
        try:
            group_by = request.args.get('group_by', 'category')
            
            if group_by not in ['category', 'month']:
                return jsonify({
                    'success': False,
                    'error': 'group_by deve ser "category" ou "month"'
                }), 400
            
            # Mapear 'month' para o formato esperado pelo serviço
            group_key = 'category' if group_by == 'category' else 'month'
            report = service.report(group_by=group_key)
            
            # Converter Money para string para serialização JSON
            report_data = {key: str(value.amount) for key, value in report.items()}
            
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

