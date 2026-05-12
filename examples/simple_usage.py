from lightdb import LightDB

# Create a new database object, or load an existing one from file
db = LightDB("db.json")

# Store a key-value pair
db.set("name", "Alice")

# Read a value
name = db.get("name")
print(name)  # Output: "Alice"

# Remove a key-value pair
db.pop("name")

# Reset the database to an empty state
db.reset()

# Persist changes to disk
db.save()
