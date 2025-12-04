from ..models import Category

class CategoryService:

    def __init__(self, category_repository):
        self.category_repository = category_repository

    def create_category(self, name, type_, user_id):

        if type_ not in ['income', 'expense']:
            raise ValueError("Tipo de categoria inválido. Deve ser 'income' ou 'expense'.")

        if self.category_repository.exists(user_id, name, type_):
            raise ValueError(f'Categoria "{name}" ({type_}) já existe para este usuário.')

        category = Category(
            name=name,
            type_=type_,
            user_id=user_id
        )

        self.category_repository.add(category)
        return category

    def update_category(self, category_id, user_id, name, type_):

        category = self.category_repository.get_by_id(category_id, user_id)

        if not category:
            raise ValueError(f'Categoria com ID "{category_id}" não encontrada.')

        # Cria um novo objeto Category com os dados atualizados para validação e persistência
        updated_category = Category(
            id_=category_id,
            name=name,
            type_=type_,
            user_id=user_id,
            created_at=category.created_at
        )

        self.category_repository.update(updated_category)
        return updated_category

    def delete_category(self, category_id, user_id):
        self.category_repository.delete(category_id, user_id)

    def get_category(self, category_id, user_id):
        return self.category_repository.get_by_id(category_id, user_id)

    def list_categories(self, user_id, type_=None):
        return self.category_repository.list_by_user(user_id, type_)

    def get_categories_grouped(self, user_id):
        categories = self.list_categories(user_id)

        grouped = {
            'income': [],
            'expense': []
        }

        for cat in categories:
            if cat.type == 'income':
                grouped['income'].append(cat)
            elif cat.type == 'expense':
                grouped['expense'].append(cat)

        grouped['income'].sort(key=lambda x: x.name)
        grouped['expense'].sort(key=lambda x: x.name)

        return grouped
