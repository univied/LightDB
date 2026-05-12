"""Primary key descriptor types for LightDB models."""

from typing import Any


class PKConfig:
    """Describes how a primary key field should be auto-generated."""

    def __init__(self, kind: str) -> None:
        self.kind = kind  # "int" | "uuid"

    def __repr__(self) -> str:
        return f"PKConfig(kind={self.kind!r})"


def int_pk() -> Any:
    """Auto-incrementing integer primary key.

    Usage::

        class User(Model, table="users", pk="id"):
            id: int = int_pk()
            name: str
    """
    return PKConfig("int")


def uuid_pk() -> Any:
    """UUID4 string primary key.

    Usage::

        class Post(Model, table="posts", pk="id"):
            id: str = uuid_pk()
            title: str
    """
    return PKConfig("uuid")
