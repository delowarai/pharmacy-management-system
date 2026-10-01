from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class Repository(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: Session):
        self.model = model
        self.session = session

    def get(self, record_id: int) -> ModelT | None:
        return self.session.get(self.model, record_id)

    def list(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        statement = select(self.model).limit(limit).offset(offset)
        return list(self.session.scalars(statement).all())

    def add(self, record: ModelT) -> ModelT:
        self.session.add(record)
        self.session.flush()
        return record

