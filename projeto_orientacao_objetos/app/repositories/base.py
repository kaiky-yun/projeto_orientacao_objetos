from abc import ABC, abstractmethod

class BaseRepository(ABC):

    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def update(self, entity):
        pass

    @abstractmethod
    def delete(self, id_):
        pass

    @abstractmethod
    def get_by_id(self, id_):
        pass

    @abstractmethod
    def list_all(self):
        pass
