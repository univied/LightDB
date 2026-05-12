"""Implementation of the Query, Condition, and FieldProxy classes for filtering and querying data."""

import operator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .fields import Field

MODEL = None  # kept for backwards-compat imports


class FieldProxy:
    """Class-level proxy for a model field that supports comparison operators returning Condition."""

    __hash__ = None  # type: ignore[assignment]

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"FieldProxy(name={self.name!r})"

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


class Query:
    """A database query builder."""

    def __init__(self, model: type[Any]) -> None:
        self.model = model
        self.conditions: list[Condition] = []

    def __repr__(self) -> str:
        return f"Query(model={self.model.__name__}, conditions={[repr(c) for c in self.conditions]})"

    def where(self, *conditions: Any, **filters: Any) -> "Query":
        """Add conditions to the query.

        Params:
            conditions: ``Condition`` objects to add
            filters: Field name / value pairs that are converted to equality conditions
        """
        self.conditions.extend(conditions)
        for field_name, value in filters.items():
            field = getattr(self.model, field_name)
            self.conditions.append(Condition(field, "==", value))
        return self

    def execute(self) -> list[Any]:
        """Execute the query and return matching instances."""
        return [m for m in self.model.all() if self.evaluate_conditions(m)]

    def evaluate_conditions(self, model: Any) -> bool:
        """Return ``True`` if *model* satisfies all conditions."""
        return all(condition.evaluate(model) for condition in self.conditions)


class Condition:
    """A single filter condition used in a query."""

    def __init__(self, field: "Field | FieldProxy", op: str, value: Any) -> None:
        self.field = field
        self.op = op
        self.value = value

    def __repr__(self) -> str:
        return f"Condition(field={self.field}, operator='{self.op}', value={self.value})"

    def evaluate(self, model: Any) -> bool:
        """Return ``True`` if the condition holds for *model*."""
        operators_map = {
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
        }
        if self.field.name is None:
            raise ValueError("Field has no name")
        value = getattr(model, self.field.name)
        return operators_map[self.op](value, self.value)
