# Models

## Defining a model

Every model class must specify:

- `table` — the key used to store records in the JSON file
- `pk` — the name of the primary key field

```python
from lightdb import LightDB, Model
from lightdb.pk import int_pk, uuid_pk

db = LightDB("db.json")

# Auto-increment integer PK
class User(Model, table="users", pk="id"):
    id: int = int_pk()
    name: str
    age: int
    tags: list[str] = []

# UUID4 string PK
class Post(Model, table="posts", pk="id"):
    id: str = uuid_pk()
    title: str
    body: str
```

## Primary key helpers

| Helper | Type | Generated value |
|--------|------|-----------------|
| `int_pk()` | `int` | `max(existing ids) + 1`, starts at `1` |
| `uuid_pk()` | `str` | UUID4 string, e.g. `"3f2504e0-..."` |

## CRUD

### Create

```python
user = User.create(name="Alice", age=30)
# id is assigned automatically
print(user.id)  # 1
```

### Read one

```python
user = User.get(name="Alice")          # keyword filter
user = User.get(User.name == "Alice")  # condition object
```

Returns `None` if not found; raises `ValueError` if more than one record matches.

### Read all

```python
all_users = User.all()
```

### Filter

```python
adults   = User.filter(User.age >= 18)
alices   = User.filter(User.name == "Alice")
combined = User.filter(User.age >= 18, User.name != "Bob")
```

Keyword shorthand (equality only):

```python
User.filter(name="Alice")
```

### Update

```python
user.name = "Kristy"
user.save()
```

### Delete

```python
user.delete()
```

## Field types

Field types are validated by [Pydantic](https://docs.pydantic.dev/). Any type that Pydantic supports can be used:

```python
class Item(Model, table="items", pk="id"):
    id: int = int_pk()
    name: str
    price: float
    tags: list[str] = []
    meta: dict[str, object] = {}
    description: str | None = None
```

## Filtering with comparison operators

Class-level field access returns a `FieldProxy` that produces `Condition` objects:

```python
User.age >= 18        # Condition(field=age, operator='>=', value=18)
User.name == "Alice"  # Condition(field=name, operator='==', value='Alice')
```

Supported operators: `==`, `!=`, `<`, `<=`, `>`, `>=`.

## Using multiple databases

Each `LightDB(...)` call sets the global current database.  
You can bind a model to a specific database explicitly:

```python
db1 = LightDB("db1.json")

class User(Model, table="users", pk="id"):
    id: int = int_pk()
    name: str

db2 = LightDB("db2.json")

User.all(use_db=db2)   # reads from db2 instead of db1
```
