from uuid import UUID

from sqlalchemy.orm import Session


class BaseRepository[ModelT]:
    """Thin persistence helpers shared by infrastructure repositories."""

    def __init__(self, session: Session, model_type: type[ModelT]) -> None:
        self._session = session
        self._model_type = model_type

    @property
    def session(self) -> Session:
        return self._session

    def get_by_id(self, entity_id: UUID) -> ModelT | None:
        return self._session.get(self._model_type, entity_id)

    def add(self, model: ModelT) -> ModelT:
        self._session.add(model)
        return model

    def delete(self, model: ModelT) -> None:
        self._session.delete(model)

    def flush(self) -> None:
        self._session.flush()

    def commit(self) -> None:
        """Prefer UnitOfWork.commit() at the application boundary."""
        self._session.commit()

    def refresh(self, model: ModelT) -> ModelT:
        self._session.refresh(model)
        return model
