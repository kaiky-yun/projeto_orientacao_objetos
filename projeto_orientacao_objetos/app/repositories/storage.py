import json
import os
from pathlib import Path
from threading import Lock

class JSONStorage:

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self._lock = Lock()

        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self._write_data({})

    def load(self):
        with self._lock:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}

    def save(self, data):
        with self._lock:
            self._write_data(data)

    def _write_data(self, data):

        if self.file_path.exists():
            backup_path = self.file_path.with_suffix('.json.bak')
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    with open(backup_path, 'w', encoding='utf-8') as bf:
                        bf.write(f.read())
            except Exception:
                pass

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
