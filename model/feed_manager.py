from abc import ABC, abstractmethod
from typing import Dict, Type, TypeVar, Any


T = TypeVar("T", bound="FeedManger")


class FeedManger(ABC):
    """
    Abstract service contract for feed management.

    Enforces Singleton behavior per concrete subclass.
    Each subclass will have exactly one instance per process.
    """

    _instances: Dict[Type["FeedManger"], "FeedManger"] = {}

    def __new__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """
        Enforce singleton per concrete subclass.
        """
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
        return cls._instances[cls]  # type: ignore

    # ─────────────────────────────────────────────
    # Abstract API
    # ─────────────────────────────────────────────

    @abstractmethod
    async def register_feed(self, url: str) -> None:
        """
        Register and begin monitoring a feed.

        Args:
            url (str): RSS/Atom feed URL
        """
        raise NotImplementedError

    @abstractmethod
    async def deregister_feed(self, url: str) -> None:
        """
        Stop monitoring a feed.

        Args:
            url (str): RSS/Atom feed URL
        """
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Gracefully release resources and stop all feeds.
        """
        raise NotImplementedError