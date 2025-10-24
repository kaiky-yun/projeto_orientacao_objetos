"""
API REST v2 com autenticação JWT para o Controlador Financeiro.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import os

from finance.models import Transaction, Money, Category
from finance.repository import JSONTransactionRepository
from finance.services import FinanceService
from finance.storage import JSONStorage
from finance.auth_models import User
from finance.auth_repository import JSONUserRepository
from finance.auth_service import AuthService
from finance.report_service import ReportService
from finance.investment_models import Investment
from finance.investment_repository import JSONInvestmentRepository
from finance.investment_service import InvestmentService
from finance.simulation_service import SimulationService
from finance.price_service import PriceService


def create_app():
    """Factory function para criar e configurar a aplicação Flask com autenticação."""
    app = Flask(__name__)
    CORS(app)
    
    # Configuração JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    jwt = JWTManager(app)
    
    # Inicializar repositórios e serviços
    storage_path = os.getenv('FINANCE_DB_PATH', os.path.expanduser('~/.finance_app/transactions.json'))
    users_path = os.getenv('USERS_DB_PATH', os.path.expanduser('~/.finance_app/users.json'))
    
    # Serviço de preços
    price_service = PriceService()
    
    transaction_storage = JSONStorage(storage_path)
    transaction_repository = JSONTransactionRepository(transaction_storage)
    finance_service = FinanceService(transaction_repository)
    
    user_storage = JSONStorage(users_path)
    user_repository = JSONUserRepository(user_storage)
    auth_service = AuthService(user_repository)
    
    report_service = ReportService(transaction_repository)
    
    investments_path = os.getenv('INVESTMENTS_DB_PATH', os.path.expanduser('~/.finance_app/investments.json'))
    investment_storage = JSONStorage(investments_path)
    investment_repository = JSONInvestmentRepository(investment_storage)
    investment_service = InvestmentService(investment_repository)
    
    # ==================== FUNÇÕES AUXILIARES ====================
    
    def parse_date(date_str, end_of_day=False):
        """Parsear string de data no formato YYYY-MM-DD."""
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str)
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            return dt
        except ValueError:
            return None
    
    def filter_transactions_by_date(transactions, start_date=None, end_date=None):
        """Filtrar transações por período de tempo."""
        if not start_date and not end_date:
            return transactions
        
        filtered = []
        for tx in transactions:
            tx_date = tx.occurred_at
            if tx_date.tzinfo is None or tx_date.tzinfo.utcoffset(tx_date) is None:
                tx_date = tx_date.replace(tzinfo=timezone.utc)
            
            if start_date and tx_date < start_date:
                continue
            if end_date and tx_date > end_date:
                continue
            
            filtered.append(tx)
        
        return filtered
    
    # ==================== ENDPOINTS DE AUTENTICAÇÃO ====================
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Registrar novo usuário."""
        try:
            data = request.get_json()
            print(f"[REGISTER] Dados recebidos: {data}")
            
            required_fields = ['username', 'email', 'password']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': f'Campos obrigatórios: {", ".join(required_fields)}'
                }), 400
            
            print(f"[REGISTER] Tentando registrar: {data['username']}")
            user = auth_service.register(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            print(f"[REGISTER] Usuário criado: {user.id}")
            
            # Criar token de acesso
            access_token = create_access_token(identity=user.id)
            print(f"[REGISTER] Token criado")
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user.to_dict(),
                    'access_token': access_token
                }
            }), 201
        
        except ValueError as e:
            print(f"[REGISTER] ValueError: {e}")
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            print(f"[REGISTER] Exception: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Autenticar usuário."""
        try:
            data = request.get_json()
            
            if 'username' not in data or 'password' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Username/email e senha são obrigatórios'
                }), 400
            
            user = auth_service.login(
                username_or_email=data['username'],
                password=data['password']
            )
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Credenciais inválidas'
                }), 401
            
            # Criar token de acesso
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user.to_dict(),
                    'access_token': access_token
                }
            }), 200
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required()
    def get_current_user():
        """Obter informações do usuário autenticado."""
        try:
            user_id = get_jwt_identity()
            user = auth_service.get_user_by_id(user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Usuário não encontrado'
                }), 404
            
            return jsonify({
                'success': True,
                'data': user.to_dict()
            }), 200
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ENDPOINTS DE TRANSAÇÕES ====================
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Verificar saúde da API."""
        return jsonify({'status': 'ok', 'message': 'API v2 com autenticação está funcionando'}), 200
    
    @app.route('/api/transactions', methods=['GET'])
    @jwt_required()
    def list_transactions():
        """Listar transações do usuário autenticado."""
        try:
            user_id = get_jwt_identity()
            transactions = finance_service.list_transactions(user_id=user_id)
            
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
    @jwt_required()
    def create_transaction():
        """Criar uma nova transação."""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            required_fields = ['type', 'amount', 'description', 'category']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': f'Campos obrigatórios: {", ".join(required_fields)}'
                }), 400
            
            if data['type'] not in ['income', 'expense']:
                return jsonify({
                    'success': False,
                    'error': 'Tipo deve ser "income" ou "expense"'
                }), 400
            
            occurred_at = None
            if 'occurred_at' in data and data['occurred_at']:
                try:
                    dt_naive = datetime.fromisoformat(data['occurred_at'])
                    occurred_at = dt_naive.replace(tzinfo=timezone.utc)
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Data inválida. Use formato ISO 8601'
                    }), 400
            
            transaction = finance_service.add_transaction(
                type=data['type'],
                amount=data['amount'],
                description=data['description'],
                category=data['category'],
                user_id=user_id,
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
    @jwt_required()
    def get_transaction(transaction_id):
        """Obter uma transação específica."""
        try:
            user_id = get_jwt_identity()
            transaction = transaction_repository.by_id(transaction_id)
            
            if not transaction:
                return jsonify({
                    'success': False,
                    'error': 'Transação não encontrada'
                }), 404
            
            # Verificar se a transação pertence ao usuário
            if transaction.user_id != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Acesso negado'
                }), 403
            
            return jsonify({
                'success': True,
                'data': transaction.to_dict()
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
    @jwt_required()
    def delete_transaction(transaction_id):
        """Deletar uma transação."""
        try:
            user_id = get_jwt_identity()
            transaction = transaction_repository.by_id(transaction_id)
            
            if not transaction:
                return jsonify({
                    'success': False,
                    'error': 'Transação não encontrada'
                }), 404
            
            # Verificar se a transação pertence ao usuário
            if transaction.user_id != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Acesso negado'
                }), 403
            
            removed = finance_service.remove(transaction_id)
            
            return jsonify({
                'success': True,
                'message': 'Transação removida com sucesso'
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/balance', methods=['GET'])
    @jwt_required()
    def get_balance():
        """Obter o saldo total do usuário."""
        try:
            user_id = get_jwt_identity()
            transactions = finance_service.list_transactions(user_id=user_id)
            
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
    @jwt_required()
    def get_report():
        """Gerar relatório agrupado por categoria ou mês."""
        try:
            user_id = get_jwt_identity()
            group_by = request.args.get('group_by', 'category')
            
            if group_by not in ['category', 'month']:
                return jsonify({
                    'success': False,
                    'error': 'group_by deve ser "category" ou "month"'
                }), 400
            
            transactions = finance_service.list_transactions(user_id=user_id)
            
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
                    tx_date_aware = tx.occurred_at
                    if tx_date_aware.tzinfo is None or tx_date_aware.tzinfo.utcoffset(tx_date_aware) is None:
                        tx_date_aware = tx_date_aware.replace(tzinfo=timezone.utc)
                    key = tx_date_aware.strftime("%Y-%m")
                
                groups[key] = groups[key] + tx.signed_amount
            
            report_data = {key: str(value.amount) for key, value in groups.items()}
            
            return jsonify({
                'success': True,
                'data': report_data,
                'group_by': group_by
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/categories', methods=['GET'])
    @jwt_required()
    def get_categories():
        """Obter lista de categorias únicas do usuário."""
        try:
            user_id = get_jwt_identity()
            transactions = finance_service.list_transactions(user_id=user_id)
            categories = sorted(set(tx.category.name for tx in transactions))
            return jsonify({
                'success': True,
                'data': categories
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ENDPOINTS DE RELATÓRIOS AVANÇADOS ====================
    
    @app.route('/api/reports/monthly-by-category', methods=['GET'])
    @jwt_required()
    def monthly_by_category_report():
        """Relatório mensal detalhado por categoria."""
        try:
            user_id = get_jwt_identity()
            
            # Parâmetros opcionais
            year = request.args.get('year', type=int)
            month = request.args.get('month', type=int)
            
            report = report_service.monthly_by_category(user_id, year, month)
            
            # Converter Money para string
            result = {}
            for month_key, categories in report.items():
                result[month_key] = {
                    cat: str(amount.amount) 
                    for cat, amount in categories.items()
                }
            
            return jsonify({
                'success': True,
                'data': result
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/reports/category-by-month', methods=['GET'])
    @jwt_required()
    def category_by_month_report():
        """Relatório de uma categoria ao longo dos meses."""
        try:
            user_id = get_jwt_identity()
            
            category = request.args.get('category')
            if not category:
                return jsonify({
                    'success': False,
                    'error': 'Parâmetro "category" é obrigatório'
                }), 400
            
            year = request.args.get('year', type=int)
            
            report = report_service.category_by_month(user_id, category, year)
            
            # Converter Money para string
            result = {month: str(amount.amount) for month, amount in report.items()}
            
            return jsonify({
                'success': True,
                'data': result,
                'category': category
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/reports/available-months', methods=['GET'])
    @jwt_required()
    def available_months():
        """Lista de meses disponíveis (com transações)."""
        try:
            user_id = get_jwt_identity()
            months = report_service.available_months(user_id)
            
            return jsonify({
                'success': True,
                'data': months
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/reports/summary-by-month', methods=['GET'])
    @jwt_required()
    def summary_by_month():
        """Resumo financeiro por mês (receitas, despesas, saldo)."""
        try:
            user_id = get_jwt_identity()
            
            year = request.args.get('year', type=int)
            month = request.args.get('month', type=int)
            
            summary = report_service.summary_by_month(user_id, year, month)
            
            return jsonify({
                'success': True,
                'data': summary
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ENDPOINTS DE INVESTIMENTOS ====================
    
    @app.route('/api/investments', methods=['GET'])
    @jwt_required()
    def list_investments():
        """Listar investimentos do usuário."""
        try:
            user_id = get_jwt_identity()
            investments = investment_service.list_user_investments(user_id)
            
            return jsonify({
                'success': True,
                'data': [inv.to_dict() for inv in investments]
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/investments', methods=['POST'])
    @jwt_required()
    def create_investment():
        """Criar um novo investimento."""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            required_fields = ['name', 'type', 'initial_amount', 'monthly_rate']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': f'Campos obrigatórios: {", ".join(required_fields)}'
                }), 400
            
            # Validar tipo
            valid_types = ['renda_fixa', 'renda_variavel', 'fundo', 'criptomoeda', 'outro']
            if data['type'] not in valid_types:
                return jsonify({
                    'success': False,
                    'error': f'Tipo deve ser um de: {", ".join(valid_types)}'
                }), 400
            
            # Parsear data de início se fornecida
            start_date = None
            if 'start_date' in data and data['start_date']:
                try:
                    dt_naive = datetime.fromisoformat(data['start_date'])
                    start_date = dt_naive.replace(tzinfo=timezone.utc)
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Data inválida. Use formato ISO 8601'
                    }), 400
            
            investment = investment_service.create_investment(
                name=data['name'],
                type=data['type'],
                initial_amount=data['initial_amount'],
                monthly_rate=float(data['monthly_rate']),
                user_id=user_id,
                current_amount=data.get('current_amount'),
                start_date=start_date,
                notes=data.get('notes', '')
            )
            
            return jsonify({
                'success': True,
                'data': investment.to_dict()
            }), 201
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/investments/<investment_id>', methods=['GET'])
    @jwt_required()
    def get_investment(investment_id):
        """Obter um investimento específico."""
        try:
            user_id = get_jwt_identity()
            investment = investment_service.get_investment(investment_id)
            
            if not investment:
                return jsonify({
                    'success': False,
                    'error': 'Investimento não encontrado'
                }), 404
            
            # Verificar se pertence ao usuário
            if investment.user_id != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Acesso negado'
                }), 403
            
            return jsonify({
                'success': True,
                'data': investment.to_dict()
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/investments/<investment_id>', methods=['PUT'])
    @jwt_required()
    def update_investment(investment_id):
        """Atualizar um investimento."""
        try:
            user_id = get_jwt_identity()
            investment = investment_service.get_investment(investment_id)
            
            if not investment:
                return jsonify({
                    'success': False,
                    'error': 'Investimento não encontrado'
                }), 404
            
            # Verificar se pertence ao usuário
            if investment.user_id != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Acesso negado'
                }), 403
            
            data = request.get_json()
            
            updated = investment_service.update_investment(
                investment_id,
                name=data.get('name'),
                current_amount=data.get('current_amount'),
                monthly_rate=data.get('monthly_rate'),
                notes=data.get('notes')
            )
            
            return jsonify({
                'success': True,
                'data': updated.to_dict()
            }), 200
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/investments/<investment_id>', methods=['DELETE'])
    @jwt_required()
    def delete_investment(investment_id):
        """Deletar um investimento."""
        try:
            user_id = get_jwt_identity()
            investment = investment_service.get_investment(investment_id)
            
            if not investment:
                return jsonify({
                    'success': False,
                    'error': 'Investimento não encontrado'
                }), 404
            
            # Verificar se pertence ao usuário
            if investment.user_id != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Acesso negado'
                }), 403
            
            investment_service.delete_investment(investment_id)
            
            return jsonify({
                'success': True,
                'message': 'Investimento removido com sucesso'
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/investments/summary', methods=['GET'])
    @jwt_required()
    def investments_summary():
        """Resumo dos investimentos do usuário."""
        try:
            user_id = get_jwt_identity()
            
            total_invested = investment_service.total_invested(user_id)
            total_current = investment_service.total_current_value(user_id)
            total_profit = investment_service.total_profit(user_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'total_invested': str(total_invested.amount),
                    'total_current_value': str(total_current.amount),
                    'total_profit': str(total_profit.amount),
                    'currency': 'BRL'
                }
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ENDPOINTS DE SIMULAÇÃO ====================
    
    @app.route('/api/simulations/fixed-contribution', methods=['POST'])
    @jwt_required()
    def simulate_fixed_contribution():
        """Simular investimento com aporte mensal fixo."""
        try:
            data = request.get_json()
            
            required_fields = ['initial_amount', 'monthly_contribution', 'monthly_rate', 'months']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': f'Campos obrigatórios: {", ".join(required_fields)}'
                }), 400
            
            result = SimulationService.simulate_fixed_contribution(
                initial_amount=data['initial_amount'],
                monthly_contribution=data['monthly_contribution'],
                monthly_rate=float(data['monthly_rate']),
                months=int(data['months'])
            )
            
            return jsonify({
                'success': True,
                'data': result.to_dict()
            }), 200
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/simulations/variable-contribution', methods=['POST'])
    @jwt_required()
    def simulate_variable_contribution():
        """Simular investimento com aportes mensais variáveis."""
        try:
            data = request.get_json()
            
            required_fields = ['initial_amount', 'monthly_contributions', 'monthly_rate']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': f'Campos obrigatórios: {", ".join(required_fields)}'
                }), 400
            
            if not isinstance(data['monthly_contributions'], list):
                return jsonify({
                    'success': False,
                    'error': 'monthly_contributions deve ser uma lista'
                }), 400
            
            result = SimulationService.simulate_variable_contribution(
                initial_amount=data['initial_amount'],
                monthly_contributions=data['monthly_contributions'],
                monthly_rate=float(data['monthly_rate'])
            )
            
            return jsonify({
                'success': True,
                'data': result.to_dict()
            }), 200
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/simulations/compare-scenarios', methods=['POST'])
    @jwt_required()
    def compare_scenarios():
        """Comparar múltiplos cenários de investimento."""
        try:
            data = request.get_json()
            
            required_fields = ['initial_amount', 'monthly_contributions', 'monthly_rate', 'months']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'success': False,
                    'error': f'Campos obrigatórios: {", ".join(required_fields)}'
                }), 400
            
            if not isinstance(data['monthly_contributions'], list):
                return jsonify({
                    'success': False,
                    'error': 'monthly_contributions deve ser uma lista'
                }), 400
            
            scenarios = SimulationService.compare_scenarios(
                initial_amount=data['initial_amount'],
                monthly_contributions=data['monthly_contributions'],
                monthly_rate=float(data['monthly_rate']),
                months=int(data['months'])
            )
            
            # Converter resultados para dict
            result = {
                scenario: simulation.to_dict()
                for scenario, simulation in scenarios.items()
            }
            
            return jsonify({
                'success': True,
                'data': result
            }), 200
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/simulations/from-investment/<investment_id>', methods=['POST'])
    @jwt_required()
    def simulate_from_investment(investment_id):
        """Simular projeção baseada em um investimento cadastrado."""
        try:
            user_id = get_jwt_identity()
            investment = investment_service.get_investment(investment_id)
            
            if not investment:
                return jsonify({
                    'success': False,
                    'error': 'Investimento não encontrado'
                }), 404
            
            # Verificar se pertence ao usuário
            if investment.user_id != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Acesso negado'
                }), 403
            
            data = request.get_json()
            
            # Parâmetros da simulação
            monthly_contribution = data.get('monthly_contribution', 0)
            months = data.get('months', 12)
            
            # Usar dados do investimento
            result = SimulationService.simulate_fixed_contribution(
                initial_amount=str(investment.current_amount.amount),
                monthly_contribution=monthly_contribution,
                monthly_rate=investment.monthly_rate,
                months=int(months)
            )
            
            return jsonify({
                'success': True,
                'data': result.to_dict(),
                'investment': investment.to_dict()
            }), 200
        
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ENDPOINTS DE COTAÇÃO ====================
    
    @app.route('/api/prices/stock/<symbol>', methods=['GET'])
    @jwt_required()
    def get_stock_price(symbol):
        """Buscar preço atual de uma ação."""
        try:
            user_id = get_jwt_identity()
            region = request.args.get('region', 'US')
            price_data = price_service.get_stock_price(symbol, region, user_id)
            
            if not price_data:
                return jsonify({
                    'success': False,
                    'error': f'Não foi possível obter cotação para {symbol}'
                }), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'symbol': price_data['symbol'],
                    'name': price_data['name'],
                    'price': float(price_data['price']),
                    'currency': price_data['currency'],
                    'exchange': price_data['exchange'],
                    'timestamp': price_data['timestamp'],
                    'day_high': float(price_data['day_high']),
                    'day_low': float(price_data['day_low']),
                    'volume': price_data['volume'],
                    'source': price_data['source']
                }
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/prices/crypto/<symbol>', methods=['GET'])
    @jwt_required()
    def get_crypto_price(symbol):
        """Buscar preço atual de uma criptomoeda."""
        try:
            price_data = price_service.get_crypto_price(symbol)
            
            if not price_data:
                return jsonify({
                    'success': False,
                    'error': f'Não foi possível obter cotação para {symbol}'
                }), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'symbol': price_data['symbol'],
                    'name': price_data['name'],
                    'price': float(price_data['price']),
                    'currency': price_data['currency'],
                    'exchange': price_data['exchange'],
                    'timestamp': price_data['timestamp'],
                    'day_high': float(price_data['day_high']),
                    'day_low': float(price_data['day_low']),
                    'volume': price_data['volume'],
                    'source': price_data['source']
                }
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/prices/search', methods=['GET'])
    @jwt_required()
    def search_symbols():
        """Buscar símbolos de ações/criptos."""
        try:
            query = request.args.get('q', '')
            
            if not query or len(query) < 2:
                return jsonify({
                    'success': False,
                    'error': 'Query deve ter pelo menos 2 caracteres'
                }), 400
            
            results = price_service.search_symbol(query)
            
            return jsonify({
                'success': True,
                'data': results
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

