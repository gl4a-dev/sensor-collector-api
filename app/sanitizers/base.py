import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T_Schema = TypeVar("T_Schema")
T_Model = TypeVar("T_Model")

logger = logging.getLogger(__name__)


class BaseSanitizer(ABC, Generic[T_Schema]):
    def __init__(self, next_sanitizer: Optional["BaseSanitizer[T_Schema]"] = None):
        self._next = next_sanitizer

    @abstractmethod
    def validate(self, item: T_Schema) -> bool:
        pass

    def handle(self, item: T_Schema) -> bool:
        if not self.validate(item):
            return False

        if self._next:
            return self._next.handle(item)

        return True


class BaseFactory(ABC, Generic[T_Schema, T_Model]):
    @abstractmethod
    def create(self, item: T_Schema) -> Optional[T_Model]:
        pass