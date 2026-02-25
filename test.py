class Person:
    name = "John"
    age = 30


person = Person()

# Get existing attribute
print(getattr(person, "name", "Unknown"))  # "John"

# Get non-existing with default
print(getattr(person, "address", "Not found"))  # "Not found"

# Without default (raises error)
# print(getattr(person, 'address'))  # AttributeError!
