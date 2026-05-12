# ruff: noqa: S101

from lightdb import LightDB, Model
from lightdb.pk import int_pk

# Initialize the database
db = LightDB("db.json")


# Define a User model with an auto-increment integer PK
class User(Model, table="users", pk="id"):
    id: int = int_pk()
    name: str
    age: int
    tags: list[str] = []


# Create a new user (id is assigned automatically)
user = User.create(name="Alice", age=30)
print(f"Created: {user}")  # User(id=1, name='Alice', age=30)

# Retrieve a user
retrieved = User.get(name="Alice")
assert retrieved is not None
print(f"Retrieved: {retrieved.name}, age {retrieved.age}")

# Update
retrieved.name = "Kristy"
retrieved.save()
print(f"Updated: {retrieved}")

# Filter with comparison operators
adults = User.filter(User.age >= 18)
print("Adults:")
for u in adults:
    print(f"  {u.name}, age {u.age}")

# Delete
retrieved.delete()
print(f"Deleted: {retrieved.name}")

# Verify deletion
gone = User.get(name="Kristy")
print(f"Still exists: {gone is not None}")
