import pytest
from decimal import Decimal
from finance.models import Money, Category, Transaction


def test_money_normaliza_duas_casas():
    assert Money(10.1).amount == Decimal("10.10")
    assert Money("3.456").amount == Decimal("3.46")


def test_category_nao_aceita_vazio():
    with pytest.raises(ValueError):
        Category("")


def test_transaction_valida_e_assinada():
    cat = Category("Teste")
    t1 = Transaction(type="income", amount=Money(100), description="ok", category=cat)
    t2 = Transaction(type="expense", amount=Money(30), description="ok", category=cat)
    assert t1.signed_amount == Money(100)
    assert t2.signed_amount == Money(-30)


def test_transaction_valida_campos_obrigatorios():
    cat = Category("Teste")
    with pytest.raises(ValueError):
        Transaction(type="x", amount=Money(10), description="ok", category=cat)
    with pytest.raises(ValueError):
        Transaction(type="income", amount=Money(0), description="ok", category=cat)
    with pytest.raises(ValueError):
        Transaction(type="income", amount=Money(10), description=" ", category=cat)
