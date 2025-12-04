from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from app.repositories import JSONStorage, TransactionRepository, CategoryRepository
from app.services import ReportService, CategoryService
from app.models import Category
from config import Config
from .auth_controller import login_required
from datetime import datetime, timezone
import calendar

report_bp = Blueprint('report', __name__, url_prefix='/reports')

transactions_storage = JSONStorage(Config.TRANSACTIONS_DB_PATH)
transaction_repository = TransactionRepository(transactions_storage)
report_service = ReportService(transaction_repository)

categories_storage = JSONStorage(Config.CATEGORIES_DB_PATH)
category_repository = CategoryRepository(categories_storage)
category_service = CategoryService(category_repository)

@report_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session.get('user_id')

    try:

        current_month_report = report_service.get_monthly_report(user_id)

        top_categories = report_service.get_top_categories(user_id, limit=5)

        yearly_summary = report_service.get_yearly_summary(user_id)

        categories = category_service.get_categories_grouped(user_id)

        return render_template(
            'reports/index.html',
            current_month_report=current_month_report,
            top_categories=top_categories,
            yearly_summary=yearly_summary,
            categories=categories
        )

    except Exception as e:
        flash(f'Erro ao gerar relatórios: {str(e)}', 'error')
        return redirect(url_for('transaction.list_transactions'))

@report_bp.route('/by-category', methods=['GET', 'POST'])
@login_required
def by_category():
    user_id = session.get('user_id')
    categories = category_service.get_categories_grouped(user_id)
    report_data = None
    filters = {}

    if request.method == 'POST':
        transaction_type = request.form.get('type', '')
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')

        try:

            start_date = None
            end_date = None

            if start_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str)
                    if start_date.tzinfo is None:
                        start_date = start_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    flash('Data inicial inválida', 'error')
                    return redirect(url_for('report.by_category'))

            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str)
                    if end_date.tzinfo is None:
                        end_date = end_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    flash('Data final inválida', 'error')
                    return redirect(url_for('report.by_category'))

            report_type = transaction_type if transaction_type else None
            report_data = report_service.get_report_by_category(
                user_id,
                transaction_type=report_type,
                start_date=start_date,
                end_date=end_date
            )

            filters = {
                'type': transaction_type,
                'start_date': start_date_str,
                'end_date': end_date_str
            }

            if not report_data:
                flash('Nenhuma transação encontrada com os filtros especificados', 'info')

        except Exception as e:
            flash(f'Erro ao gerar relatório: {str(e)}', 'error')

    return render_template(
        'reports/by_category.html',
        report_data=report_data,
        filters=filters,
        categories=categories
    )

@report_bp.route('/monthly', methods=['GET', 'POST'])
@login_required
def monthly():
    user_id = session.get('user_id')
    categories = category_service.get_categories_grouped(user_id)
    report_data = None
    selected_month = None
    selected_year = None

    if request.method == 'POST':
        year_str = request.form.get('year', '')
        month_str = request.form.get('month', '')
        transaction_type = request.form.get('type', '')

        try:
            year = int(year_str) if year_str else datetime.now(timezone.utc).year
            month = int(month_str) if month_str else datetime.now(timezone.utc).month

            if month < 1 or month > 12:
                flash('Mês inválido', 'error')
                return redirect(url_for('report.monthly'))

            report_type = transaction_type if transaction_type else None
            report_data = report_service.get_monthly_report(
                user_id,
                year=year,
                month=month,
                transaction_type=report_type
            )

            selected_month = month
            selected_year = year

        except ValueError:
            flash('Ano ou mês inválido', 'error')
        except Exception as e:
            flash(f'Erro ao gerar relatório: {str(e)}', 'error')

    current_year = datetime.now(timezone.utc).year
    years = list(range(current_year - 5, current_year + 1))

    return render_template(
        'reports/monthly.html',
        report_data=report_data,
        selected_month=selected_month,
        selected_year=selected_year,
        years=years,
        months=list(range(1, 13)),
        month_names={i: calendar.month_name[i] for i in range(1, 13)},
        categories=categories
    )

@report_bp.route('/period', methods=['GET', 'POST'])
@login_required
def period():
    user_id = session.get('user_id')
    categories = category_service.get_categories_grouped(user_id)
    report_data = None
    filters = {}

    if request.method == 'POST':
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        transaction_type = request.form.get('type', '')

        if not start_date_str or not end_date_str:
            flash('Data inicial e final são obrigatórias', 'error')
            return redirect(url_for('report.period'))

        try:

            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)

            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)

            if start_date > end_date:
                flash('Data inicial não pode ser maior que data final', 'error')
                return redirect(url_for('report.period'))

            report_type = transaction_type if transaction_type else None
            report_data = report_service.get_period_report(
                user_id,
                start_date=start_date,
                end_date=end_date,
                transaction_type=report_type
            )

            filters = {
                'start_date': start_date_str,
                'end_date': end_date_str,
                'type': transaction_type
            }

            if not report_data['transactions']:
                flash('Nenhuma transação encontrada no período especificado', 'info')

        except ValueError as e:
            flash(f'Data inválida: {str(e)}', 'error')
        except Exception as e:
            flash(f'Erro ao gerar relatório: {str(e)}', 'error')

    return render_template(
        'reports/period.html',
        report_data=report_data,
        filters=filters,
        categories=categories
    )

@report_bp.route('/yearly', methods=['GET', 'POST'])
@login_required
def yearly():
    user_id = session.get('user_id')
    report_data = None
    selected_year = None

    if request.method == 'POST':
        year_str = request.form.get('year', '')

        try:
            year = int(year_str) if year_str else datetime.now(timezone.utc).year

            report_data = report_service.get_yearly_summary(user_id, year=year)
            selected_year = year

        except ValueError:
            flash('Ano inválido', 'error')
        except Exception as e:
            flash(f'Erro ao gerar relatório: {str(e)}', 'error')

    current_year = datetime.now(timezone.utc).year
    years = list(range(current_year - 5, current_year + 1))

    return render_template(
        'reports/yearly.html',
        report_data=report_data,
        selected_year=selected_year,
        years=years,
        month_names={i: calendar.month_abbr[i] for i in range(1, 13)}
    )

@report_bp.route('/category-trend/<category_name>', methods=['GET', 'POST'])
@login_required
def category_trend(category_name):
    user_id = session.get('user_id')
    categories = category_service.get_categories_grouped(user_id)
    trend_data = None
    months = 12

    try:

        all_categories = categories.get('income', []) + categories.get('expense', [])
        if category_name not in all_categories:
            flash('Categoria não encontrada', 'error')
            return redirect(url_for('report.index'))

        if request.method == 'POST':
            months_str = request.form.get('months', '12')
            try:
                months = int(months_str)
                if months < 1 or months > 60:
                    months = 12
            except ValueError:
                months = 12

        trend_data = report_service.get_category_trend(
            user_id,
            category_name,
            months=months
        )

        if not trend_data:
            flash(f'Nenhuma transação encontrada para a categoria "{category_name}"', 'info')

    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'error')
        return redirect(url_for('report.index'))

    return render_template(
        'reports/category_trend.html',
        category_name=category_name,
        trend_data=trend_data,
        months=months,
        categories=categories
    )
