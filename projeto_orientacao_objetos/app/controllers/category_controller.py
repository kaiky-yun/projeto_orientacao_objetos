from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.repositories import JSONStorage, CategoryRepository
from app.services import CategoryService
from config import Config
from .auth_controller import login_required

category_bp = Blueprint('category', __name__, url_prefix='/categories')

categories_storage = JSONStorage(Config.CATEGORIES_DB_PATH)
category_repository = CategoryRepository(categories_storage)
category_service = CategoryService(category_repository)

@category_bp.route('/', methods=['GET'])
@login_required
def list_categories():
    user_id = session.get('user_id')

    try:
        categories_grouped = category_service.get_categories_grouped(user_id)

        return render_template(
            'categories/list.html',
            categories_grouped=categories_grouped
        )

    except Exception as e:
        flash(f'Erro ao listar categorias: {str(e)}', 'error')
        return redirect(url_for('transaction.list_transactions'))

@category_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_category():
    user_id = session.get('user_id')

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        type_ = request.form.get('type', '').strip()

        if not name or not type_:
            flash('Nome e tipo são obrigatórios', 'error')
            return redirect(url_for('category.create_category'))

        if type_ not in ['income', 'expense']:
            flash('Tipo inválido. Deve ser Receita ou Despesa.', 'error')
            return redirect(url_for('category.create_category'))

        try:
            category = category_service.create_category(
                name=name,
                type_=type_,
                user_id=user_id
            )

            flash(f'Categoria "{name}" criada com sucesso!', 'success')
            return redirect(url_for('category.list_categories'))

        except ValueError as e:
            flash(f'Erro ao criar categoria: {str(e)}', 'error')
        except Exception as e:
            flash(f'Erro inesperado: {str(e)}', 'error')

    return render_template('categories/create.html')

@category_bp.route('/<category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    user_id = session.get('user_id')

    try:
        category = category_service.get_category(category_id, user_id)

        if not category:
            flash('Categoria não encontrada', 'error')
            return redirect(url_for('category.list_categories'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            type_ = request.form.get('type', '').strip()

            if not name or not type_:
                flash('Nome e tipo são obrigatórios', 'error')
                return redirect(url_for('category.edit_category', category_id=category_id))

            if type_ not in ['income', 'expense']:
                flash('Tipo inválido. Deve ser Receita ou Despesa.', 'error')
                return redirect(url_for('category.edit_category', category_id=category_id))

            try:
                updated_category = category_service.update_category(
                    category_id,
                    user_id,
                    name=name,
                    type_=type_
                )

                flash('Categoria atualizada com sucesso!', 'success')
                return redirect(url_for('category.list_categories'))

            except ValueError as e:
                flash(f'Erro ao atualizar categoria: {str(e)}', 'error')
            except Exception as e:
                flash(f'Erro inesperado: {str(e)}', 'error')

        return render_template(
            'categories/edit.html',
            category=category
        )

    except Exception as e:
        flash(f'Erro ao editar categoria: {str(e)}', 'error')
        return redirect(url_for('category.list_categories'))

@category_bp.route('/<category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    user_id = session.get('user_id')

    try:
        category = category_service.get_category(category_id, user_id)

        if not category:
            flash('Categoria não encontrada', 'error')
            return redirect(url_for('category.list_categories'))

        category_service.delete_category(category_id, user_id)
        flash('Categoria removida com sucesso!', 'success')

    except Exception as e:
        flash(f'Erro ao remover categoria: {str(e)}', 'error')

    return redirect(url_for('category.list_categories'))

@category_bp.route('/api/list', methods=['GET'])
@login_required
def get_categories_api():
    user_id = session.get('user_id')
    type_ = request.args.get('type')

    try:
        categories = category_service.list_categories(user_id, type_)

        return jsonify({
            'success': True,
            'categories': [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'type': cat.type
                }
                for cat in categories
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
