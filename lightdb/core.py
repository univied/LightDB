"""Main implementation of the LightDB database management system"""

import json
from pathlib import Path
from typing import Any


class LightDB(dict):
    """A lightweight database implemented as a dictionary with JSON file storage.

    Extends the built-in ``dict`` to provide a simple key-value store
    that persists its data in a JSON file.
    """

    _current_db: "LightDB | None" = None

    def __init__(self, location: str) -> None:
        """Initialize the LightDB object.

        Params:
            location (``str``): Path to the JSON file where the database is stored
        """
        super().__init__()
        self.location = Path(location)
        self.update(**self._load())
        LightDB._current_db = self

    @classmethod
    def current(cls) -> "LightDB":
        """Return the current LightDB instance.

        Raises:
            ValueError: If no database has been initialized yet
        """
        if cls._current_db is None:
            raise ValueError("No current database has been set")
        return cls._current_db

    def __repr__(self) -> str:
        return f"<LightDB: {self.location}>"

    def _load(self) -> dict[str, Any]:
        if not self.location.exists():
            return {}
        with self.location.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self) -> None:
        """Persist the current state of the database to a JSON file."""
        with self.location.open("w", encoding="utf-8") as file:
            json.dump(self, file, ensure_ascii=False, indent=4)

    def set(self, key: str, value: Any) -> None:
        """Set a key-value pair in the database."""
        self[key] = value

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        """Return the value for *key*, or *default* if the key does not exist."""
        return super().get(key, default)

    def pop(self, key: str, *args: Any) -> Any:  # type: ignore[override]
        """Remove and return the value associated with *key*."""
        return super().pop(key, *args)

    def reset(self) -> None:
        """Clear all entries from the database."""
        self.clear()
