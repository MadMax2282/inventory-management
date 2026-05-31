from abc import ABC, abstractmethod


class IRepository(ABC):

    @abstractmethod
    def add(self, entity):
        raise NotImplementedError

    @abstractmethod
    def get(self, entity_id):
        raise NotImplementedError

    @abstractmethod
    def get_all(self):
        raise NotImplementedError

    @abstractmethod
    def update(self, entity):
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id):
        raise NotImplementedError

    @abstractmethod
    def exists(self, entity_id):
        raise NotImplementedError

    @abstractmethod
    def find(self, predicate):
        raise NotImplementedError
