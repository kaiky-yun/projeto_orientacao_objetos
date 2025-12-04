from .base import BaseRepository
from ..models import Category

class CategoryRepository(BaseRepository):

    def __init__(self, storage):
        self.storage = storage

    def add(self, category):
        if not isinstance(category, Category):
            raise ValueError('Objeto deve ser uma instância de Category')

        data = self.storage.load()

        if category.user_id not in data:
            data[category.user_id] = []

        # Verifica se a categoria já existe para o usuário (pelo nome e tipo)
        for cat in data[category.user_id]:
            if cat['name'].lower() == category.name.lower() and cat['type'] == category.type:
                raise ValueError(f'Categoria "{category.name}" ({category.type}) já existe para este usuário')

        data[category.user_id].append(category.to_dict())
        self.storage.save(data)

    def update(self, category):
        if not isinstance(category, Category):
            raise ValueError('Objeto deve ser uma instância de Category')

        data = self.storage.load()

        if category.user_id not in data:
            raise ValueError('Categoria não encontrada')

        # Verifica se o novo nome/tipo já existe em outra categoria (exceto a que está sendo atualizada)
        for cat in data[category.user_id]:
            if cat['id'] != category.id and \
               cat['name'].lower() == category.name.lower() and \
               cat['type'] == category.type:
                raise ValueError(f'Categoria "{category.name}" ({category.type}) já existe para este usuário')

        found = False
        for i, cat in enumerate(data[category.user_id]):
            if cat['id'] == category.id:
                data[category.user_id][i] = category.to_dict()
                found = True
                break

        if not found:
            raise ValueError('Categoria não encontrada')

        self.storage.save(data)

    def delete(self, category_id, user_id):

        data = self.storage.load()

        if user_id not in data:
            raise ValueError('Categoria não encontrada')

        found = False
        for i, cat in enumerate(data[user_id]):
            if cat['id'] == category_id:
                data[user_id].pop(i)
                found = True
                break

        if not found:
            raise ValueError('Categoria não encontrada')

        self.storage.save(data)

    def get_by_id(self, category_id, user_id):
        data = self.storage.load()

        if user_id not in data:
            return None

        for cat_data in data[user_id]:
            if cat_data['id'] == category_id:
                return Category.from_dict(cat_data)

        return None

    def list_by_user(self, user_id, type_=None):
        data = self.storage.load()

        if user_id not in data:
            return []

        categories = [Category.from_dict(cat) for cat in data[user_id]]

        if type_:
            return [cat for cat in categories if cat.type == type_]

        return categories

    def exists(self, user_id, name, type_):
        categories = self.list_by_user(user_id, type_)
        return any(cat.name.lower() == name.lower() for cat in categories)

    def list_all(self):
        data = self.storage.load()
        all_categories = []

        for user_id, categories in data.items():
            for cat_data in categories:
                all_categories.append(Category.from_dict(cat_data))

        return all_categories
