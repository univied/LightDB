# Quick start

## Database (key-value store)

```python
from lightdb import LightDB

db = LightDB("db.json")

# Store values
db.set("name", "Alice")
db.set("scores", [10, 20, 30])

# Read values
print(db.get("name"))      # "Alice"
print(db.get("missing"))   # None
print(db.get("missing", "default"))  # "default"

# Remove a key
db.pop("name")

# Persist to disk
db.save()

# Wipe everything
db.reset()
db.save()
```

## Models (structured data)

```python
from lightdb import LightDB, Model
from lightdb.pk import int_pk

db = LightDB("db.json")

class User(Model, table="users", pk="id"):
    id: int = int_pk()   # auto-increment
    name: str
    age: int

# Create
alice = User.create(name="Alice", age=30)
print(alice)  # User(id=1, name='Alice', age=30)

# Read
user = User.get(name="Alice")

# Update
user.name = "Kristy"
user.save()

# Filter
adults = User.filter(User.age >= 18)

# Delete
user.delete()
```
