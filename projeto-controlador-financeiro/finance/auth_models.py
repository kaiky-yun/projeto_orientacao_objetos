"""
Modelos de autenticação para o sistema de controle financeiro.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import bcrypt


@dataclass(slots=True)
class User:
    """Representa um usuário do sistema."""
    username: str
    email: str
    password_hash: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not self.username or not self.username.strip():
            raise ValueError("Nome de usuário obrigatório")
        if not self.email or not self.email.strip():
            raise ValueError("Email obrigatório")
        if "@" not in self.email:
            raise ValueError("Email inválido")
        if not self.password_hash:
            raise ValueError("Hash de senha obrigatório")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash bcrypt da senha."""
        if not password or len(password) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verifica se a senha corresponde ao hash armazenado."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self) -> dict:
        """Serializa usuário para dicionário (sem senha)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }
    
    def to_dict_with_password(self) -> dict:
        """Serializa usuário completo (incluindo hash de senha)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at.isoformat(),
        }
    
    @staticmethod
    def from_dict(d: dict) -> User:
        """Deserializa usuário de dicionário."""
        return User(
            id=d["id"],
            username=d["username"],
            email=d["email"],
            password_hash=d["password_hash"],
            created_at=datetime.fromisoformat(d["created_at"]),
        )

