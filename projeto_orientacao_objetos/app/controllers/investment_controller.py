from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.repositories import JSONStorage, InvestmentRepository
from app.services import InvestmentService
from app.models import Investment
from config import Config
from .auth_controller import login_required
from datetime import datetime, timezone

investment_bp = Blueprint('investment', __name__, url_prefix='/investments')

investments_storage = JSONStorage(Config.INVESTMENTS_DB_PATH)
investment_repository = InvestmentRepository(investments_storage)
investment_service = InvestmentService(investment_repository)

@investment_bp.route('/', methods=['GET'])
@login_required
def list_investments():
    user_id = session.get('user_id')

    try:
        investments = investment_service.list_investments(user_id)

        investments.sort(key=lambda inv: inv.start_date, reverse=True)

        total_invested = investment_service.get_total_invested(user_id)
        total_current = investment_service.get_total_current_value(user_id)
        total_profit = investment_service.get_total_profit(user_id)

        investment_types = Investment.VALID_TYPES

        return render_template(
            'investments/list.html',
            investments=investments,
            total_invested=total_invested,
            total_current=total_current,
            total_profit=total_profit,
            investment_types=investment_types
        )

    except Exception as e:
        flash(f'Erro ao listar investimentos: {str(e)}', 'error')
        return redirect(url_for('auth.logout'))

@investment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_investment():
    user_id = session.get('user_id')
    investment_types = Investment.VALID_TYPES

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        type_ = request.form.get('type', '').strip()
        initial_amount = request.form.get('initial_amount', '')
        current_amount = request.form.get('current_amount', '')
        monthly_rate = request.form.get('monthly_rate', '')
        notes = request.form.get('notes', '').strip()
        start_date_str = request.form.get('start_date', '')

        if not name or not type_ or not initial_amount or not current_amount or monthly_rate == '':
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('investment.create_investment'))

        if type_ not in Investment.VALID_TYPES:
            flash('Tipo de investimento inválido', 'error')
            return redirect(url_for('investment.create_investment'))

        try:

            start_date = None
            if start_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str)
                    if start_date.tzinfo is None:
                        start_date = start_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    flash('Data inválida', 'error')
                    return redirect(url_for('investment.create_investment'))

            investment = investment_service.create_investment(
                name=name,
                type_=type_,
                initial_amount=float(initial_amount),
                current_amount=float(current_amount),
                monthly_rate=float(monthly_rate),
                user_id=user_id,
                start_date=start_date,
                notes=notes
            )

            flash('Investimento criado com sucesso!', 'success')
            return redirect(url_for('investment.list_investments'))

        except ValueError as e:
            flash(f'Erro ao criar investimento: {str(e)}', 'error')
        except Exception as e:
            flash(f'Erro inesperado: {str(e)}', 'error')

    return render_template('investments/create.html', investment_types=investment_types)

@investment_bp.route('/<investment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_investment(investment_id):
    user_id = session.get('user_id')
    investment_types = Investment.VALID_TYPES

    try:
        investment = investment_service.get_investment(investment_id, user_id)

        if not investment:
            flash('Investimento não encontrado', 'error')
            return redirect(url_for('investment.list_investments'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            type_ = request.form.get('type', '').strip()
            initial_amount = request.form.get('initial_amount', '')
            current_amount = request.form.get('current_amount', '')
            monthly_rate = request.form.get('monthly_rate', '')
            notes = request.form.get('notes', '').strip()
            start_date_str = request.form.get('start_date', '')

            if not name or not type_ or not initial_amount or not current_amount or monthly_rate == '':
                flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
                return redirect(url_for('investment.edit_investment', investment_id=investment_id))

            try:

                start_date = None
                if start_date_str:
                    try:
                        start_date = datetime.fromisoformat(start_date_str)
                        if start_date.tzinfo is None:
                            start_date = start_date.replace(tzinfo=timezone.utc)
                    except ValueError:
                        flash('Data inválida', 'error')
                        return redirect(url_for('investment.edit_investment', investment_id=investment_id))

                updated_investment = investment_service.update_investment(
                    investment_id,
                    user_id,
                    name=name,
                    type=type_,
                    initial_amount=float(initial_amount),
                    current_amount=float(current_amount),
                    monthly_rate=float(monthly_rate),
                    start_date=start_date,
                    notes=notes
                )

                flash('Investimento atualizado com sucesso!', 'success')
                return redirect(url_for('investment.list_investments'))

            except ValueError as e:
                flash(f'Erro ao atualizar investimento: {str(e)}', 'error')
            except Exception as e:
                flash(f'Erro inesperado: {str(e)}', 'error')

        return render_template(
            'investments/edit.html',
            investment=investment,
            investment_types=investment_types
        )

    except Exception as e:
        flash(f'Erro ao editar investimento: {str(e)}', 'error')
        return redirect(url_for('investment.list_investments'))

@investment_bp.route('/<investment_id>/delete', methods=['POST'])
@login_required
def delete_investment(investment_id):
    user_id = session.get('user_id')

    try:
        investment = investment_service.get_investment(investment_id, user_id)

        if not investment:
            flash('Investimento não encontrado', 'error')
            return redirect(url_for('investment.list_investments'))

        investment_service.delete_investment(investment_id, user_id)
        flash('Investimento removido com sucesso!', 'success')

    except Exception as e:
        flash(f'Erro ao remover investimento: {str(e)}', 'error')

    return redirect(url_for('investment.list_investments'))
