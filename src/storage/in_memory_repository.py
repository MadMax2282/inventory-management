from src.storage.base_repository import IRepository
from src.utils.exceptions import DuplicateEntityError, EntityNotFoundError


class InMemoryRepository(IRepository):

    def __init__(self):
        self._items = {}

    def add(self, entity):
        if entity.id in self._items:
            raise DuplicateEntityError(
                "Сутність з id {} вже існує".format(entity.id)
            )
        self._items[entity.id] = entity
        return entity

    def get(self, entity_id):
        entity = self._items.get(entity_id)
        if entity is None:
            raise EntityNotFoundError("Сутність з id {} не знайдено".format(entity_id))
        return entity

    def get_all(self):
        return list(self._items.values())

    def update(self, entity):
        if entity.id not in self._items:
            raise EntityNotFoundError(
                "Неможливо оновити: id {} не знайдено".format(entity.id)
            )
        self._items[entity.id] = entity
        return entity

    def delete(self, entity_id):
        if entity_id not in self._items:
            raise EntityNotFoundError(
                "Неможливо видалити: id {} не знайдено".format(entity_id)
            )
        del self._items[entity_id]

    def exists(self, entity_id):
        return entity_id in self._items

    def find(self, predicate):
        return [item for item in self._items.values() if predicate(item)]

    def count(self):
        return len(self._items)

    def clear(self):
        self._items.clear()
