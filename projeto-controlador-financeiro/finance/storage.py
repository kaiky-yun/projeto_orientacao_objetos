from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any


class JSONStorage:
    """Persistência simples em arquivo JSON."""
    def __init__(self, file_path: str | os.PathLike | None = None):
        default_path = Path.home() / ".finance_app" / "transactions.json"
        self.file_path = Path(file_path or default_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write({"transactions": []})

    def _read(self) -> dict[str, Any]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict[str, Any]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list[dict]:
        return self._read().get("transactions", [])

    def save_all(self, transactions: list[dict]) -> None:
        self._write({"transactions": transactions})
