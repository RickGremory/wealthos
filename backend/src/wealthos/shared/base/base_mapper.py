from abc import ABC, abstractmethod


class BaseMapper[ModelT, EntityT](ABC):
    """Convert between persistence models and domain entities."""

    @abstractmethod
    def to_entity(self, model: ModelT) -> EntityT:
        raise NotImplementedError

    @abstractmethod
    def to_model(self, entity: EntityT) -> ModelT:
        raise NotImplementedError
