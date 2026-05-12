# Changelog

## 3.0.0 - by [univied](https://github.com/univied)

### Added
- Pydantic v2 as the validation backend — `Model` now extends `pydantic.BaseModel`
- `int_pk()` — auto-increment integer primary key helper
- `uuid_pk()` — UUID4 string primary key helper
- `pk=` class keyword argument on `Model` to declare the primary key field name
- `FieldProxy` — class-level field proxy enabling `User.age >= 20` filter syntax
- `lightdb.pk` module (`PKConfig`, `int_pk`, `uuid_pk`)
- `FieldProxy` and `Condition` exported from the top-level `lightdb` package
- Markdown-only documentation (`docs/`) replacing the previous Sphinx/RTD setup
- `CHANGELOG.md` in the project root

### Changed
- **Breaking:** `Model` no longer uses a custom `Field` descriptor for validation; Pydantic handles all type checking
- **Breaking:** models now require a `pk=` keyword argument specifying the primary key field; the implicit `_id` field is gone
- **Breaking:** Python 3.12+ is now the minimum required version
- All type annotations migrated to native syntax (`dict`, `list`, `X | None`) — `typing.Dict/List/Optional/Union` removed throughout
- `MODEL` TypeVar removed from public API (kept as `None` stub for backwards compatibility)
- `Field` class retained as a standalone legacy utility; it is no longer used internally by `Model`
- Documentation rebuilt from scratch as plain Markdown — no Sphinx, no `conf.py`, no `.rst` files
- `CHANGELOG.rst` replaced by `CHANGELOG.md`

### Fixed
- All basedpyright errors resolved
- All ruff lint errors resolved

---

## 2.0

### Added
- `models.py` — model implementation
- `fields.py` — field implementation and validation
- `query.py` — query execution on model data
- `exceptions.py` — custom exceptions
- Tests for LightDB and models
- `examples/models_usage.py`

---

## 1.4.0

- Renamed `LightDB.py` → `core.py`
- Updated license

---

## 1.3.3

- Rewrote code and docstrings
- Rewrote README
- Added tests

---

## 1.3.2

### Fixed
- Error when getting a non-string key

---

## 1.3.1

### Fixed
- Encoding error on save

---

## 1.3

### Added
- Methods `set_key()`, `get_key()`, `pop_key()`

---

## 1.2

- Code refactor

---

## 1.1

### Added
- `LightDB` subclasses `dict`

### Fixed
- Fatal error caused by recursive function call

---

## 1.0

### Added
- Initial `LightDB` class
