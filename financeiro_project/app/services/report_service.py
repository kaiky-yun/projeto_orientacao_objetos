from datetime import datetime, timedelta, timezone
from collections import defaultdict
from ..models import Money

class ReportService:

    def __init__(self, transaction_repository):
        self.transaction_repository = transaction_repository

    def get_report_by_category(self, user_id, transaction_type=None, start_date=None, end_date=None):
        transactions = self.transaction_repository.list_by_user(user_id)

        if transaction_type:
            transactions = [tx for tx in transactions if tx.type == transaction_type]

        if start_date or end_date:
            transactions = self._filter_by_date_range(transactions, start_date, end_date)

        report = defaultdict(lambda: Money(0))

        for tx in transactions:
            category_name = tx.category.name
            report[category_name] = report[category_name] + tx.amount

        report_dict = dict(report)
        sorted_report = dict(sorted(
            report_dict.items(),
            key=lambda x: x[1].amount,
            reverse=True
        ))

        return sorted_report

    def get_monthly_report(self, user_id, year=None, month=None, transaction_type=None):
        if year is None:
            year = datetime.now(timezone.utc).year
        if month is None:
            month = datetime.now(timezone.utc).month

        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)

        transactions = self.transaction_repository.list_by_user(user_id)

        if transaction_type:
            transactions = [tx for tx in transactions if tx.type == transaction_type]

        transactions = self._filter_by_date_range(transactions, start_date, end_date)

        income_total = Money(0)
        expense_total = Money(0)

        for tx in transactions:
            if tx.type == 'income':
                income_total = income_total + tx.amount
            else:
                expense_total = expense_total + tx.amount

        balance = income_total - expense_total

        return {
            'year': year,
            'month': month,
            'month_name': self._get_month_name(month),
            'income_total': income_total,
            'expense_total': expense_total,
            'balance': balance,
            'transaction_count': len(transactions),
            'transactions': sorted(transactions, key=lambda x: x.occurred_at, reverse=True)
        }

    def get_period_report(self, user_id, start_date, end_date, transaction_type=None):
        transactions = self.transaction_repository.list_by_user(user_id)

        if transaction_type:
            transactions = [tx for tx in transactions if tx.type == transaction_type]

        transactions = self._filter_by_date_range(transactions, start_date, end_date)

        income_total = Money(0)
        expense_total = Money(0)

        for tx in transactions:
            if tx.type == 'income':
                income_total = income_total + tx.amount
            else:
                expense_total = expense_total + tx.amount

        balance = income_total - expense_total

        categories_report = defaultdict(lambda: Money(0))
        for tx in transactions:
            category_name = tx.category.name
            categories_report[category_name] = categories_report[category_name] + tx.amount

        return {
            'start_date': start_date,
            'end_date': end_date,
            'income_total': income_total,
            'expense_total': expense_total,
            'balance': balance,
            'transaction_count': len(transactions),
            'transactions': sorted(transactions, key=lambda x: x.occurred_at, reverse=True),
            'by_category': dict(sorted(
                dict(categories_report).items(),
                key=lambda x: x[1].amount,
                reverse=True
            ))
        }

    def get_yearly_summary(self, user_id, year=None):
        if year is None:
            year = datetime.now(timezone.utc).year

        monthly_data = []

        for month in range(1, 13):
            report = self.get_monthly_report(user_id, year, month)
            monthly_data.append({
                'month': month,
                'month_name': report['month_name'],
                'income': report['income_total'],
                'expense': report['expense_total'],
                'balance': report['balance']
            })

        year_income = Money(0)
        year_expense = Money(0)

        for month_data in monthly_data:
            year_income = year_income + month_data['income']
            year_expense = year_expense + month_data['expense']

        year_balance = year_income - year_expense

        return {
            'year': year,
            'income_total': year_income,
            'expense_total': year_expense,
            'balance': year_balance,
            'monthly_data': monthly_data
        }

    def get_category_trend(self, user_id, category_name, months=12):
        transactions = self.transaction_repository.list_by_user(user_id)

        transactions = [tx for tx in transactions if tx.category.name == category_name]

        monthly_totals = defaultdict(lambda: Money(0))

        for tx in transactions:
            month_key = tx.occurred_at.strftime('%Y-%m')
            monthly_totals[month_key] = monthly_totals[month_key] + tx.amount

        sorted_months = sorted(monthly_totals.items())

        if len(sorted_months) > months:
            sorted_months = sorted_months[-months:]

        return [
            {
                'month': month,
                'total': total,
                'formatted_month': self._format_month_key(month)
            }
            for month, total in sorted_months
        ]

    def get_top_categories(self, user_id, limit=5, transaction_type=None):
        transactions = self.transaction_repository.list_by_user(user_id)
        
        if transaction_type:
            transactions = [tx for tx in transactions if tx.type == transaction_type]

        report = defaultdict(lambda: {'total': Money(0), 'type': None})

        for tx in transactions:
            category_name = tx.category.name
            # O tipo da categoria é o mesmo tipo da transação
            report[category_name]['total'] = report[category_name]['total'] + tx.amount
            report[category_name]['type'] = tx.category.type

        # Converte para lista de tuplas (category_name, total, type)
        report_list = [
            (name, data['total'], data['type'])
            for name, data in report.items()
        ]

        # Ordena por total
        sorted_report = sorted(
            report_list,
            key=lambda x: x[1].amount,
            reverse=True
        )

        top_items = sorted_report[:limit]

        return [
            {
                'category': category,
                'total': total,
                'type': type_
            }
            for category, total, type_ in top_items
        ]

    def _filter_by_date_range(self, transactions, start_date, end_date):
        filtered = transactions

        if start_date:
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            filtered = [tx for tx in filtered if tx.occurred_at >= start_date]

        if end_date:
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            filtered = [tx for tx in filtered if tx.occurred_at <= end_date]

        return filtered

    def _get_month_name(self, month):
        months = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }
        return months.get(month, 'Desconhecido')

    def _format_month_key(self, month_key):
        try:
            date = datetime.strptime(month_key, '%Y-%m')
            return date.strftime('%b/%Y').capitalize()
        except:
            return month_key


