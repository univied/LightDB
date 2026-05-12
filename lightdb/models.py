"""Implementation of the pydantic-based Model class for database management."""

import types
import typing
import uuid
from typing import Any, Self

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field as PydanticField
from pydantic import model_validator
from pydantic._internal._model_construction import ModelMetaclass

from .core import LightDB
from .exceptions import NoArgsProvidedError
from .pk import PKConfig
from .query import Condition, FieldProxy, Query

MODEL = None  # kept for backwards-compat imports


def _prepare_model_attrs(attrs: dict[str, Any], table: str | None, pk: str | None) -> None:
    """Validate table/pk kwargs and scan for PKConfig sentinels in the namespace dict."""
    if not table:
        raise ValueError("`table` is required for model classes")
    if not isinstance(table, str):
        raise TypeError(f"`table` must be of type `str` (`{type(table)}` given)")

    attrs["__table__"] = table

    if not attrs.get("__db__"):
        attrs["__db__"] = LightDB.current()

    pk_field_name: str | None = pk
    pk_kind: str | None = None

    # Detect PKConfig markers — replace sentinel with a real pydantic Field(default=None).
    # We intentionally do NOT touch __annotations__ here; on Python 3.14+ annotations live
    # in annotationlib and are inaccessible as a namespace dict key before class creation.
    # PK value injection happens in the model_validator on Model.
    for field_name, field_default in list(attrs.items()):
        if isinstance(field_default, PKConfig):
            if pk_field_name is None:
                pk_field_name = field_name
            pk_kind = field_default.kind
            attrs[field_name] = PydanticField(default=None)

    attrs["__pk__"] = pk_field_name
    attrs["__pk_kind__"] = pk_kind


def _widen_pk_annotation(cls: type, attrs: dict[str, Any]) -> None:
    """Widen the PK field annotation to ``type | None`` after class creation.

    This allows pydantic to accept ``None`` at construction time so that the
    ``_inject_pk`` model validator can fill in the generated value.
    """
    pk_field_name = attrs.get("__pk__")
    pk_kind = attrs.get("__pk_kind__")
    if pk_field_name and pk_kind:
        ann = cls.__annotations__
        if pk_field_name in ann:
            original_type = ann[pk_field_name]
            if not _is_optional(original_type):
                cls.__annotations__[pk_field_name] = original_type | None
                cls.model_rebuild(force=True)


def _is_optional(tp: Any) -> bool:
    """Return True if *tp* already includes ``None`` (i.e. is a union with ``NoneType``)."""
    origin = getattr(tp, "__origin__", None)
    # Handle `X | None` (types.UnionType, Python 3.10+) and `Optional[X]` (typing.Union)
    if origin is types.UnionType or origin is typing.Union:
        return type(None) in tp.__args__
    return tp is type(None)


class LightDBMeta(ModelMetaclass):
    """Metaclass for Model — adds table/pk kwargs, field proxies, and auto-pk logic."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
        table: str | None = None,
        pk: str | None = None,
        **kwargs: Any,
    ) -> type:
        if name != "Model":
            _prepare_model_attrs(attrs, table, pk)

        cls = super().__new__(mcs, name, bases, attrs, **kwargs)

        # Post-creation: widen PK annotation to `type | None` so pydantic accepts None
        # at construction time (before the model_validator injects the actual PK value).
        # Modifying __annotations__ on the *class* (not the namespace dict) works on all
        # Python versions, including 3.14+ where annotations use annotationlib.
        if name != "Model":
            _widen_pk_annotation(cls, attrs)

        return cls

    def __getattr__(self, name: str) -> FieldProxy:  # noqa: N805
        """Return a FieldProxy for class-level attribute access (enables User.age >= 20)."""
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            annotations: dict[str, Any] = object.__getattribute__(self, "__annotations__")
        except AttributeError:
            annotations = {}
        if name in annotations:
            return FieldProxy(name)
        raise AttributeError(f"type object '{self.__name__}' has no attribute '{name}'")


class Model(PydanticBaseModel, metaclass=LightDBMeta):
    """Base model class for interacting with data in a LightDB database."""

    model_config = {"arbitrary_types_allowed": True}

    __table__: str | None = None
    __db__: LightDB | None = None
    __pk__: str | None = None
    __pk_kind__: str | None = None

    def __init_subclass__(cls, table: str | None = None, pk: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

    @model_validator(mode="before")
    @classmethod
    def _inject_pk(cls, data: Any) -> Any:
        """Auto-generate PK value before pydantic validates the model."""
        pk_field = cls.__pk__
        pk_kind = cls.__pk_kind__
        if not pk_field or not pk_kind:
            return data
        if not isinstance(data, dict):
            return data
        if data.get(pk_field) is not None:
            return data
        if pk_kind == "uuid":
            data = {**data, pk_field: str(uuid.uuid4())}
        elif pk_kind == "int":
            data = {**data, pk_field: cls._compute_next_int_pk()}
        return data

    @classmethod
    def _compute_next_int_pk(cls) -> int:
        """Return the next auto-increment integer PK for this model."""
        pk_field = cls.__pk__
        rows = cls.__db__.get(cls.__table__, [])  # type: ignore[union-attr]
        if not rows:
            return 1
        return max(row.get(pk_field, 0) for row in rows) + 1

    def __repr__(self) -> str:
        fields_info = ", ".join(f"{k}={v!r}" for k, v in self.model_dump().items())
        return f"{self.__class__.__name__}({fields_info})"

    @classmethod
    def create(cls, **kwargs: Any) -> Self:
        """Create and persist a new model instance.

        Params:
            kwargs: Field names and their values
        """
        if not kwargs:
            raise NoArgsProvidedError("No `kwargs` were provided")

        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    def get(cls, *args: Any, **kwargs: Any) -> Self | None:
        """Return a single instance matching the filter criteria.

        Raises:
            NoArgsProvidedError: If no filters were given
            ValueError: If more than one match is found
        """
        if not (args or kwargs):
            raise NoArgsProvidedError("No `args` or `kwargs` were provided")

        results = cls.filter(*args, **kwargs)
        if not results:
            return None

        if len(results) > 1:
            raise ValueError(f"Multiple instances of `{cls.__name__}` model found by the specified filters")

        return results[0]

    def save(self) -> None:
        """Persist the current state of this instance to the database."""
        pk_field = self.__class__.__pk__
        if pk_field:
            existing = self.__class__.get(**{pk_field: getattr(self, pk_field)})
            if existing:
                existing.delete()

        new_data = self.model_dump()
        self.__db__.setdefault(self.__table__, []).append(new_data)  # type: ignore[union-attr]
        self.__db__.save()  # type: ignore[union-attr]

    def delete(self) -> None:
        """Delete this instance from the database."""
        pk_field = self.__class__.__pk__
        rows = self.__db__.get(self.__table__, [])  # type: ignore[union-attr]
        pk_value = getattr(self, pk_field) if pk_field else None

        for item in rows:
            if pk_field and item.get(pk_field) == pk_value:
                rows.remove(item)
                self.__db__.save()  # type: ignore[union-attr]
                return

    @classmethod
    def filter(cls, *args: Any, **kwargs: Any) -> list[Self]:
        """Return all instances matching the filter criteria.

        Raises:
            NoArgsProvidedError: If no filters were given
        """
        if not (args or kwargs):
            raise NoArgsProvidedError("No `args` or `kwargs` were provided")

        query = Query(cls)
        query.where(*args, **kwargs)
        return query.execute()

    @classmethod
    def all(cls, use_db: LightDB | None = None) -> list[Self]:
        """Return all instances of this model from the database."""
        return [cls(**row) for row in (use_db or cls.__db__).get(cls.__table__, [])]  # type: ignore[union-attr]
