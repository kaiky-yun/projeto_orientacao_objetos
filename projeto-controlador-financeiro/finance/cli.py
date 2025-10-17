from __future__ import annotations

import argparse
from typing import Optional
from datetime import datetime
from decimal import Decimal, InvalidOperation

from .repository import JSONTransactionRepository
from .services import FinanceService
from .models import Transaction, Money


def fmt_money(d) -> str:
    """Formata Money ou Decimal/float para pt-BR."""
    return (
        f"R$ {d.amount if hasattr(d, 'amount') else d:,.2f}"
        .replace(",", "X").replace(".", ",").replace("X", ".")
    )


def print_tx(tx: Transaction, idx: Optional[int] = None) -> None:
    """Imprime uma transação em linha única, com IDX opcional."""
    prefix = f"[{idx}] " if idx is not None else ""
    print(
        f"{prefix}{tx.id[:8]} | {tx.occurred_at:%Y-%m-%d} | {tx.type:<7} | "
        f"{fmt_money(tx.amount):>12} | {tx.category.name:<15} | {tx.description}"
    )


def ask(prompt: str, *, required: bool = True, default: Optional[str] = None) -> str:
    """Entrada com validação e valor padrão."""
    while True:
        msg = f"{prompt}"
        if default is not None:
            msg += f" [{default}]"
        msg += ": "
        ans = input(msg).strip()
        if not ans and default is not None:
            return default
        if ans or not required:
            return ans
        print("⚠️  Campo obrigatório. Tente novamente.")


def ask_amount(prompt: str = "Valor (use ponto para centavos, ex: 45.90)") -> str:
    """Pergunta um valor monetário válido (como string)."""
    while True:
        s = ask(prompt)
        try:
            Decimal(str(s))
            return s
        except (InvalidOperation, ValueError):
            print("⚠️  Valor inválido. Ex: 120.00")


def ask_type() -> str:
    """Pergunta o tipo (income/expense) aceitando 1/2 e termos em PT."""
    while True:
        t = ask("Tipo (1=Receita | 2=Despesa)", default="2")
        if t in ("1", "income", "receita"):
            return "income"
        if t in ("2", "expense", "despesa"):
            return "expense"
        print("⚠️  Opção inválida. Responda 1 (Receita) ou 2 (Despesa).")


def parse_multi_indices(s: str) -> list[int]:
    """
    Converte entrada tipo "1 2 3", "1,2,3" ou "1-3 7" para lista de ints.
    Remove duplicados preservando a ordem.
    """
    parts = [p for chunk in s.replace(",", " ").split() for p in chunk.split()]
    indices: list[int] = []
    for p in parts:
        if "-" in p:
            a, b = p.split("-", 1)
            if a.isdigit() and b.isdigit():
                a, b = int(a), int(b)
                if a <= b:
                    indices.extend(list(range(a, b + 1)))
        elif p.isdigit():
            indices.append(int(p))
    seen: set[int] = set()
    out: list[int] = []
    for i in indices:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def interactive_loop() -> None:
    repo = JSONTransactionRepository()
    svc = FinanceService(repo)

    MENU = """
================= FINANCE CONTROL =================
1) Ver saldo
2) Listar lançamentos
3) Adicionar lançamento
4) Relatório por categoria
5) Relatório por mês
6) Remover lançamentos
7) Sair
===================================================
"""
    while True:
        print(MENU)
        opt = ask("Escolha uma opção", default="2")

        if opt == "1":
            print("\nSaldo:", fmt_money(svc.balance()), "\n")
            input("Pressione Enter para continuar...")

        elif opt == "2":
            items = svc.list_transactions()
            if not items:
                print("\nNenhuma transação cadastrada.\n")
            else:
                print("\nIDX/ID   | Data       | Tipo    |      Valor | Categoria       | Descrição")
                print("-" * 90)
                for i, tx in enumerate(items):
                    print_tx(tx, idx=i)
                print()
            input("Pressione Enter para continuar...")

        elif opt == "3":
            t = ask_type()
            amount = ask_amount()
            desc = ask("Descrição")
            cat = ask("Categoria (ex: Alimentação, Transporte, Trabalho)")
            tx = svc.add_transaction(type=t, amount=amount, description=desc, category=cat)
            print("\n✅ Lançamento adicionado:")
            print_tx(tx)
            input("\nPressione Enter para continuar...")

        elif opt == "4":
            data = svc.report(group_by="category")
            print("\nRelatório por categoria:")
            for key, value in sorted(data.items()):
                print(f"- {key}: {fmt_money(value)}")
            print()
            input("Pressione Enter para continuar...")

        elif opt == "5":
            data = svc.report(group_by="month")
            print("\nRelatório por mês:")
            for key, value in sorted(data.items()):
                print(f"- {key}: {fmt_money(value)}")
            print()
            input("Pressione Enter para continuar...")

        elif opt == "6":
            # ✅ agora remove QUALQUER lançamento (income ou expense)
            items = svc.list_transactions()
            if not items:
                print("\nNão há lançamentos para remover.\n")
                input("Pressione Enter para continuar...")
                continue

            print("\nSelecione um ou mais lançamentos pelo [IDX] (ex: 0 2 5 ou 0-3):")
            print("IDX/ID   | Data       | Tipo    |      Valor | Categoria       | Descrição")
            print("-" * 90)
            for i, tx in enumerate(items):
                print_tx(tx, idx=i)

            while True:
                sel = ask("Digite os IDX a remover (ou deixe vazio para cancelar)", required=False)
                if sel == "":
                    break

                indices = parse_multi_indices(sel)
                if not indices:
                    print("⚠️  Nenhum índice válido informado.")
                    continue

                removidos = 0
                # remove em ordem reversa para não invalidar os índices
                for i in sorted(set(indices), reverse=True):
                    if 0 <= i < len(items):
                        if svc.remove(items[i].id):
                            removidos += 1

                print(f"✅ Removidos: {removidos}")
                break

            print()
            input("Pressione Enter para continuar...")

        elif opt == "7":
            print("\nAté mais!")
            break
        else:
            print("⚠️  Opção inválida. Tente novamente.\n")


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(prog="finance-cli", description="Controle financeiro - OOP/CLI")
    sub = parser.add_subparsers(dest="cmd")

    # Subcomandos (modo antigo) continuam disponíveis
    p_add = sub.add_parser("add", help="Adicionar transação")
    p_add.add_argument("--type", choices=["income", "expense"], required=True)
    p_add.add_argument("--amount", required=True, type=str)
    p_add.add_argument("--desc", required=True, type=str)
    p_add.add_argument("--category", required=True, type=str)

    sub.add_parser("list", help="Listar transações")
    sub.add_parser("balance", help="Exibir saldo")

    p_report = sub.add_parser("report", help="Relatórios")
    p_report.add_argument("--by", choices=["category", "month"], default="category")

    p_remove = sub.add_parser("remove", help="Remover transação (por ID)")
    p_remove.add_argument("--id", required=True)

    args = parser.parse_args(argv)
    if args.cmd is None:
        interactive_loop()
        return

    svc = FinanceService(JSONTransactionRepository())

    if args.cmd == "add":
        tx = svc.add_transaction(type=args.type, amount=args.amount, description=args.desc, category=args.category)
        print("Transação adicionada:")
        print_tx(tx)

    elif args.cmd == "list":
        items = svc.list_transactions()
        if not items:
            print("Nenhuma transação.")
        else:
            print("ID       | Data       | Tipo    |      Valor | Categoria       | Descrição")
            print("-" * 85)
            for tx in items:
                print_tx(tx)

    elif args.cmd == "balance":
        print("Saldo:", fmt_money(svc.balance()))

    elif args.cmd == "report":
        data = svc.report(group_by=args.by)
        print(f"Relatório por {args.by}:")
        for key, value in sorted(data.items()):
            print(f"- {key}: {fmt_money(value)}")

    elif args.cmd == "remove":
        ok = svc.remove(args.id)
        print("Removido." if ok else "ID não encontrado.")


if __name__ == "__main__":
    main()
