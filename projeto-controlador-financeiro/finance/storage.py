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
            # Criar arquivo vazio baseado no nome
            if "transactions" in str(self.file_path):
                self._write({"transactions": []})
            else:
                # Para outros arquivos (users, investments), usar lista vazia
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)

    def _read(self) -> dict[str, Any] | list[dict]:
        """Lê dados do arquivo JSON."""
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Se for lista, retornar como dict com chave genérica para compatibilidade
            if isinstance(data, list):
                return {"data": data}
            return data

    def _write(self, data: dict[str, Any]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list[dict]:
        return self._read().get("transactions", [])

    def save_all(self, transactions: list[dict]) -> None:
        self._write({"transactions": transactions})
    
    # Métodos genéricos para uso em outros repositórios
    def load(self) -> list[dict]:
        """Carrega dados do arquivo JSON como lista."""
        data = self._read()
        
        # Se for o formato antigo com chave "transactions", retornar a lista
        if "transactions" in data:
            return data["transactions"]
        
        # Se tiver chave "data" (lista convertida), retornar a lista
        if "data" in data:
            return data["data"]
        
        # Se for dict vazio ou sem chaves conhecidas, retornar lista vazia
        return []
    
    def save(self, data: list[dict]) -> None:
        """Salva lista de dados no arquivo JSON."""
        # Verificar se o arquivo atual usa formato com chave "transactions"
        try:
            current = self._read()
            if "transactions" in current:
                # Manter formato antigo
                self._write({"transactions": data})
                return
        except:
            pass
        
        # Usar formato de lista direta
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
