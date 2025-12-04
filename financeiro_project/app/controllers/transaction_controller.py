from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.repositories import JSONStorage, TransactionRepository, CategoryRepository
from app.services import FinanceService, CategoryService
from app.models import Category
from config import Config
from .auth_controller import login_required
from datetime import datetime, timezone

transaction_bp = Blueprint('transaction', __name__, url_prefix='/transactions')

transactions_storage = JSONStorage(Config.TRANSACTIONS_DB_PATH)
transaction_repository = TransactionRepository(transactions_storage)
finance_service = FinanceService(transaction_repository)

categories_storage = JSONStorage(Config.CATEGORIES_DB_PATH)
category_repository = CategoryRepository(categories_storage)
category_service = CategoryService(category_repository)

@transaction_bp.route('/', methods=['GET'])
@login_required
def list_transactions():
    user_id = session.get('user_id')

    try:
        transactions = finance_service.list_transactions(user_id)

        transactions.sort(key=lambda tx: tx.occurred_at, reverse=True)

        balance = finance_service.get_balance(user_id)
        income_total = finance_service.get_income_total(user_id)
        expense_total = finance_service.get_expense_total(user_id)

        # Agora as categorias são dinâmicas, não mais estáticas
        categories = category_service.get_categories_grouped(user_id)

        return render_template(
            'transactions/list.html',
            transactions=transactions,
            balance=balance,
            income_total=income_total,
            expense_total=expense_total,
            categories=categories
        )

    except Exception as e:
        flash(f'Erro ao listar transações: {str(e)}', 'error')
        return redirect(url_for('auth.logout'))

@transaction_bp.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    user_id = session.get('user_id')
    type_ = request.args.get('type')

    try:
        categories = category_service.list_categories(user_id, type_)

        return jsonify([
            {
                'id': cat.id,
                'name': cat.name,
                'type': cat.type
            }
            for cat in categories
        ])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_transaction():
    user_id = session.get('user_id')
    categories = category_service.get_categories_grouped(user_id)

    if request.method == 'POST':
        type_ = request.form.get('type', '').strip()
        amount = request.form.get('amount', '')
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category', '').strip() # Agora recebemos o ID da categoria
        occurred_at_str = request.form.get('occurred_at', '')

        if not type_ or not amount or not description or not category_id:
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('transaction.create_transaction'))

        if type_ not in ['income', 'expense']:
            flash('Tipo inválido', 'error')
            return redirect(url_for('transaction.create_transaction'))

        try:
            # Busca o objeto Category pelo ID
            category_obj = category_service.get_category(category_id, user_id)
            if not category_obj:
                flash('Categoria selecionada inválida', 'error')
                return redirect(url_for('transaction.create_transaction'))

            occurred_at = None
            if occurred_at_str:
                try:
                    occurred_at = datetime.fromisoformat(occurred_at_str)
                    if occurred_at.tzinfo is None:
                        occurred_at = occurred_at.replace(tzinfo=timezone.utc)
                except ValueError:
                    flash('Data inválida', 'error')
                    return redirect(url_for('transaction.create_transaction'))

            transaction = finance_service.create_transaction(
                type_=type_,
                amount=float(amount),
                description=description,
                category=category_obj.name, # Passa o nome da categoria para o service
                user_id=user_id,
                occurred_at=occurred_at
            )

            flash(f'Transação criada com sucesso!', 'success')
            return redirect(url_for('transaction.list_transactions'))

        except ValueError as e:
            flash(f'Erro ao criar transação: {str(e)}', 'error')
        except Exception as e:
            flash(f'Erro inesperado: {str(e)}', 'error')

    return render_template('transactions/create.html', categories=categories)

@transaction_bp.route('/<transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    user_id = session.get('user_id')
    categories = category_service.get_categories_grouped(user_id)

    try:
        transaction = finance_service.get_transaction(transaction_id, user_id)

        if not transaction:
            flash('Transação não encontrada', 'error')
            return redirect(url_for('transaction.list_transactions'))

        if request.method == 'POST':
            type_ = request.form.get('type', '').strip()
            amount = request.form.get('amount', '')
            description = request.form.get('description', '').strip()
            category_id = request.form.get('category', '').strip() # Agora recebemos o ID da categoria
            occurred_at_str = request.form.get('occurred_at', '')

            if not type_ or not amount or not description or not category_id:
                flash('Todos os campos são obrigatórios', 'error')
                return redirect(url_for('transaction.edit_transaction', transaction_id=transaction_id))

            try:
                # Busca o objeto Category pelo ID
                category_obj = category_service.get_category(category_id, user_id)
                if not category_obj:
                    flash('Categoria selecionada inválida', 'error')
                    return redirect(url_for('transaction.edit_transaction', transaction_id=transaction_id))

                occurred_at = None
                if occurred_at_str:
                    try:
                        occurred_at = datetime.fromisoformat(occurred_at_str)
                        if occurred_at.tzinfo is None:
                            occurred_at = occurred_at.replace(tzinfo=timezone.utc)
                    except ValueError:
                        flash('Data inválida', 'error')
                        return redirect(url_for('transaction.edit_transaction', transaction_id=transaction_id))

                updated_transaction = finance_service.update_transaction(
                    transaction_id,
                    user_id,
                    type=type_,
                    amount=float(amount),
                    description=description,
                    category=category_obj.name, # Passa o nome da categoria para o service
                    occurred_at=occurred_at
                )

                flash('Transação atualizada com sucesso!', 'success')
                return redirect(url_for('transaction.list_transactions'))

            except ValueError as e:
                flash(f'Erro ao atualizar transação: {str(e)}', 'error')
            except Exception as e:
                flash(f'Erro inesperado: {str(e)}', 'error')

        return render_template(
            'transactions/edit.html',
            transaction=transaction,
            categories=categories
        )

    except Exception as e:
        flash(f'Erro ao editar transação: {str(e)}', 'error')
        return redirect(url_for('transaction.list_transactions'))

@transaction_bp.route('/<transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    user_id = session.get('user_id')

    try:
        transaction = finance_service.get_transaction(transaction_id, user_id)

        if not transaction:
            flash('Transação não encontrada', 'error')
            return redirect(url_for('transaction.list_transactions'))

        finance_service.delete_transaction(transaction_id, user_id)
        flash('Transação removida com sucesso!', 'success')

    except Exception as e:
        flash(f'Erro ao remover transação: {str(e)}', 'error')

    return redirect(url_for('transaction.list_transactions'))
