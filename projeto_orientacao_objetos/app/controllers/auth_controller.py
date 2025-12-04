from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.repositories import JSONStorage, UserRepository
from app.services import AuthService
from config import Config
import os

auth_bp = Blueprint('auth', __name__)

users_storage = JSONStorage(Config.USERS_DB_PATH)
user_repository = UserRepository(users_storage)
auth_service = AuthService(user_repository)

@auth_bp.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect(url_for('transaction.list_transactions'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        if not username_or_email or not password:
            flash('Username/email e senha são obrigatórios', 'error')
            return redirect(url_for('auth.login'))

        try:
            user = auth_service.login(username_or_email, password)

            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                session['email'] = user.email
                flash(f'Bem-vindo, {user.username}!', 'success')
                return redirect(url_for('transaction.list_transactions'))
            else:
                flash('Credenciais inválidas', 'error')

        except Exception as e:
            flash(f'Erro ao fazer login: {str(e)}', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        if not username or not email or not password:
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('auth.register'))

        if password != password_confirm:
            flash('As senhas não correspondem', 'error')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Senha deve ter pelo menos 6 caracteres', 'error')
            return redirect(url_for('auth.register'))

        try:
            user = auth_service.register(username, email, password)
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))

        except ValueError as e:
            flash(f'Erro ao cadastrar: {str(e)}', 'error')
        except Exception as e:
            flash(f'Erro inesperado: {str(e)}', 'error')

    return render_template('auth/register.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('auth.login'))

def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function
