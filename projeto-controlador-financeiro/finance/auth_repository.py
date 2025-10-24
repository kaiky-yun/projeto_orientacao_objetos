"""
Repositório para gerenciar usuários.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from .auth_models import User
from .storage import JSONStorage


class IUserRepository(ABC):
    """Interface para repositório de usuários."""
    
    @abstractmethod
    def add(self, user: User) -> None:
        """Adiciona um novo usuário."""
        pass
    
    @abstractmethod
    def by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID."""
        pass
    
    @abstractmethod
    def by_username(self, username: str) -> Optional[User]:
        """Busca usuário por nome de usuário."""
        pass
    
    @abstractmethod
    def by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
        pass
    
    @abstractmethod
    def list(self) -> list[User]:
        """Lista todos os usuários."""
        pass
    
    @abstractmethod
    def update(self, user: User) -> bool:
        """Atualiza um usuário existente."""
        pass
    
    @abstractmethod
    def remove(self, user_id: str) -> bool:
        """Remove um usuário pelo ID."""
        pass


class JSONUserRepository(IUserRepository):
    """Implementação de repositório de usuários usando JSONStorage."""
    
    def __init__(self, storage: JSONStorage):
        self.storage = storage
    
    def add(self, user: User) -> None:
        """Adiciona um novo usuário."""
        data = self.storage.load()
        
        # Verificar se username já existe
        if any(u["username"] == user.username for u in data):
            raise ValueError(f"Nome de usuário '{user.username}' já está em uso")
        
        # Verificar se email já existe
        if any(u["email"] == user.email for u in data):
            raise ValueError(f"Email '{user.email}' já está em uso")
        
        data.append(user.to_dict_with_password())
        self.storage.save(data)
    
    def by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID."""
        data = self.storage.load()
        for item in data:
            if item["id"] == user_id:
                return User.from_dict(item)
        return None
    
    def by_username(self, username: str) -> Optional[User]:
        """Busca usuário por nome de usuário."""
        data = self.storage.load()
        for item in data:
            if item["username"] == username:
                return User.from_dict(item)
        return None
    
    def by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
        data = self.storage.load()
        for item in data:
            if item["email"] == email:
                return User.from_dict(item)
        return None
    
    def list(self) -> list[User]:
        """Lista todos os usuários."""
        data = self.storage.load()
        return [User.from_dict(item) for item in data]
    
    def update(self, user: User) -> bool:
        """Atualiza um usuário existente."""
        data = self.storage.load()
        for i, item in enumerate(data):
            if item["id"] == user.id:
                data[i] = user.to_dict_with_password()
                self.storage.save(data)
                return True
        return False
    
    def remove(self, user_id: str) -> bool:
        """Remove um usuário pelo ID."""
        data = self.storage.load()
        original_len = len(data)
        data = [item for item in data if item["id"] != user_id]
        if len(data) < original_len:
            self.storage.save(data)
            return True
        return False

