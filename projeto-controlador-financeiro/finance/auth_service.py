"""
Serviço de autenticação para gerenciar usuários e login.
"""

from __future__ import annotations
from typing import Optional
from .auth_models import User
from .auth_repository import IUserRepository


class AuthService:
    """Serviço para gerenciar autenticação e usuários."""
    
    def __init__(self, repo: IUserRepository):
        self.repo = repo
    
    def register(self, username: str, email: str, password: str) -> User:
        """
        Registra um novo usuário.
        
        Args:
            username: Nome de usuário único
            email: Email único
            password: Senha em texto plano (será hasheada)
        
        Returns:
            User: Usuário criado
        
        Raises:
            ValueError: Se dados forem inválidos ou usuário já existir
        """
        # Validar senha
        if not password or len(password) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        
        # Criar hash da senha
        password_hash = User.hash_password(password)
        
        # Criar usuário
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            password_hash=password_hash
        )
        
        # Adicionar ao repositório (validará unicidade)
        self.repo.add(user)
        
        return user
    
    def login(self, username_or_email: str, password: str) -> Optional[User]:
        """
        Autentica um usuário.
        
        Args:
            username_or_email: Nome de usuário ou email
            password: Senha em texto plano
        
        Returns:
            User: Usuário autenticado ou None se credenciais inválidas
        """
        # Buscar usuário por username ou email
        user = self.repo.by_username(username_or_email)
        if not user:
            user = self.repo.by_email(username_or_email.lower())
        
        # Verificar se usuário existe e senha está correta
        if user and user.verify_password(password):
            return user
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID."""
        return self.repo.by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Busca usuário por nome de usuário."""
        return self.repo.by_username(username)
    
    def list_users(self) -> list[User]:
        """Lista todos os usuários."""
        return self.repo.list()

