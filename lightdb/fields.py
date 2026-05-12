"""Implementation of the Field class for data validation and storage"""

import types
from typing import TYPE_CHECKING, Any, get_args, get_origin

from .exceptions import ValidationError
from .query import Condition

if TYPE_CHECKING:
    from .models import LightDBMeta, Model


class Field:
    """A single typed field in a data model."""

    # __eq__ is overridden to return Condition, so we disable hashing explicitly
    __hash__ = None  # type: ignore[assignment]

    def __init__(
        self,
        name: str | None = None,
        value: Any = None,
        annotation: Any = None,
        default: Any = None,
    ) -> None:
        self.name = name
        self.annotation = annotation
        self.value = value
        self.default = default

    def __repr__(self) -> str:
        return f"Field(name={self.name}, annotation={self.annotation}, value={self.value}, default={self.default})"

    def _validate_list(self, value: list, args: tuple) -> None:
        item_type = args[0] if args else None
        if item_type is None:
            return
        for item in value:
            if not isinstance(item, item_type):
                raise ValidationError(
                    f"Expected element of type `{item_type.__name__}` in list "
                    f"for field `{self.name}`, got `{type(item).__name__}`",
                )

    def _validate_dict(self, value: dict, args: tuple) -> None:
        key_type = args[0] if args else None
        value_type = args[1] if len(args) > 1 else None
        for k, v in value.items():
            if key_type is not None and not isinstance(k, key_type):
                raise ValidationError(
                    f"Expected key of type `{key_type.__name__}` in dict "
                    f"for field `{self.name}`, got `{type(k).__name__}`",
                )
            if value_type is not None and not isinstance(v, value_type):
                raise ValidationError(
                    f"Expected value of type `{value_type.__name__}` in dict "
                    f"for field `{self.name}`, got `{type(v).__name__}`",
                )

    def _validate_union(self, value: Any, args: tuple) -> None:
        if value is None and type(None) in args:
            return
        non_none = [a for a in args if a is not type(None)]
        if not any(isinstance(value, t) for t in non_none):
            names = " | ".join(t.__name__ for t in non_none)
            raise ValidationError(
                f"Expected value of type `{names}` for field `{self.name}`, "
                f"got `{type(value).__name__}`",
            )

    def _validate_origin(self, value: Any, origin: Any, args: tuple, expected_type: Any) -> None:
        if origin is None:
            if not isinstance(value, expected_type):
                raise ValidationError(
                    f"Expected value of type `{expected_type.__name__}` for field `{self.name}`, "
                    f"got `{type(value).__name__}`",
                )
        elif origin is list:
            if not isinstance(value, list):
                raise ValidationError(
                    f"Expected value of type `list` for field `{self.name}`, "
                    f"got `{type(value).__name__}`",
                )
            self._validate_list(value, args)
        elif origin is dict:
            if not isinstance(value, dict):
                raise ValidationError(
                    f"Expected value of type `dict` for field `{self.name}`, "
                    f"got `{type(value).__name__}`",
                )
            self._validate_dict(value, args)
        else:
            raise ValidationError(
                f"Unsupported type annotation `{expected_type}` for field `{self.name}`",
            )

    def validate(self, value: Any = None) -> None:
        """Validate *value* against the field's type annotation.

        Params:
            value (``Any``, optional): Value to validate; falls back to ``self.value``
        """
        if not self.annotation:
            return

        value = value if value is not None else self.value
        expected_type = self.annotation
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        if isinstance(expected_type, types.UnionType):
            self._validate_union(value, args)
            return

        self._validate_origin(value, origin, args, expected_type)

    def __get__(self, instance: "Model", owner: "LightDBMeta") -> Any:
        if instance is None:
            return self
        return self.value

    def __set__(self, instance: "Model", value: Any) -> None:
        self.validate(value)
        self.value = value

    def __eq__(self, other: object) -> "Condition":  # type: ignore[override]
        return Condition(self, "==", other)

    def __ne__(self, other: object) -> "Condition":  # type: ignore[override]
        return Condition(self, "!=", other)

    def __lt__(self, other: Any) -> "Condition":
        return Condition(self, "<", other)

    def __le__(self, other: Any) -> "Condition":
        return Condition(self, "<=", other)

    def __gt__(self, other: Any) -> "Condition":
        return Condition(self, ">", other)

    def __ge__(self, other: Any) -> "Condition":
        return Condition(self, ">=", other)
