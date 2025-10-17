from datetime import datetime, timezone
from finance.services import FinanceService
from finance.repository import JSONTransactionRepository
from finance.storage import JSONStorage

N = 1000  # aumente para 5000/10000 se quiser um teste mais "pesado"

def make_service(tmp_path):
    # usa um arquivo temporário só para o benchmark
    storage = JSONStorage(file_path=tmp_path / "bench.json")
    repo = JSONTransactionRepository(storage)
    svc = FinanceService(repo)
    for i in range(N):
        svc.add_transaction(
            type="expense" if i % 2 == 0 else "income",
            amount=10.0 + i,
            description=f"Teste {i}",
            category="Geral",
            occurred_at=datetime.now(timezone.utc),
        )
    return svc

def test_balance_benchmark(benchmark, tmp_path):
    svc = make_service(tmp_path)
    result = benchmark(svc.balance)  # mede só o método balance()
    assert hasattr(result, "amount")

def test_report_benchmark(benchmark, tmp_path):
    svc = make_service(tmp_path)
    result = benchmark(lambda: svc.report("category"))
    assert isinstance(result, dict)
