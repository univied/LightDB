# API reference

## `lightdb.core.LightDB`

A `dict` subclass that persists its contents to a JSON file.

```python
LightDB(location: str)
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `set` | `set(key, value)` | Store a value under `key` |
| `get` | `get(key, default=None)` | Return value for `key`, or `default` |
| `pop` | `pop(key, *args)` | Remove and return value for `key` |
| `save` | `save()` | Write current state to the JSON file |
| `reset` | `reset()` | Clear all entries (call `save()` to persist) |
| `current` | `LightDB.current()` | Return the most recently created `LightDB` instance |

---

## `lightdb.models.Model`

Base class for structured data models. Backed by Pydantic.

**Class keyword arguments:**

| Kwarg | Type | Description |
|-------|------|-------------|
| `table` | `str` | JSON key used to store records *(required)* |
| `pk` | `str` | Name of the primary key field *(required)* |

**Class methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `create` | `create(**kwargs) → Self` | Create and persist a new instance |
| `get` | `get(*conditions, **filters) → Self \| None` | Return a single matching instance |
| `filter` | `filter(*conditions, **filters) → list[Self]` | Return all matching instances |
| `all` | `all(use_db=None) → list[Self]` | Return all instances |

**Instance methods:**

| Method | Description |
|--------|-------------|
| `save()` | Persist current state to the database |
| `delete()` | Remove this instance from the database |

---

## `lightdb.pk`

Primary key helper functions.

```python
from lightdb.pk import int_pk, uuid_pk
```

| Function | Returns | Description |
|----------|---------|-------------|
| `int_pk()` | `PKConfig` | Auto-increment integer PK (1, 2, 3, …) |
| `uuid_pk()` | `PKConfig` | UUID4 string PK |

---

## `lightdb.query`

### `FieldProxy`

Returned by class-level field access (e.g. `User.age`). Supports comparison operators that produce `Condition` objects.

```python
User.age >= 18   # → Condition
User.name == "Alice"
```

### `Condition`

```python
Condition(field, op, value)
```

A single filter predicate. `op` is one of `==`, `!=`, `<`, `<=`, `>`, `>=`.

### `Query`

```python
query = Query(Model)
query.where(*conditions, **filters)
results = query.execute()
```

---

## `lightdb.fields.Field`

> **Legacy.** Used by the standalone `Field` API; model validation is now handled by Pydantic.

```python
Field(name=None, value=None, annotation=None, default=None)
```

| Method | Description |
|--------|-------------|
| `validate(value=None)` | Validate a value against the field's type annotation |

---

## `lightdb.exceptions`

| Exception | Bases | Raised when |
|-----------|-------|-------------|
| `ValidationError` | `TypeError` | A field value fails type validation |
| `FieldNotFoundError` | `ValueError` | A referenced field does not exist in the table |
| `NoArgsProvidedError` | `TypeError` | A method that requires arguments is called with none |
