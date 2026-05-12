import os
import pytest

from lightdb.core import LightDB
from lightdb.models import Model
from lightdb.pk import int_pk


@pytest.fixture
def user_model():
    test_db_location = "test_db.json"
    db = LightDB(test_db_location)

    class User(Model, table="users", pk="id"):
        id: int = int_pk()
        name: str
        age: int
        items: list[str] = []
        extra: dict[str, object] = {}

    yield User
    if os.path.exists(test_db_location):
        os.remove(test_db_location)


def test_model_initialization(user_model: type):
    model = user_model(name="John", age=30)
    assert model.name == "John"
    assert model.age == 30


def test_model_save(user_model: type):
    db = user_model.__db__
    model = user_model(name="John", age=30)
    model.save()

    assert len(db.get("users")) == 1
    assert db.get("users")[0]["name"] == "John"


def test_model_get(user_model: type):
    user_model.create(name="John", age=30)
    fetched_model = user_model.get(name="John")

    assert fetched_model is not None
    assert fetched_model.name == "John"
    assert fetched_model.age == 30


def test_model_delete(user_model: type):
    model = user_model.create(name="John", age=30)
    model.delete()

    assert user_model.get(name="John") is None


def test_model_filter(user_model: type):
    user_model.create(name="John", age=30)
    user_model.create(name="Jane", age=25)

    results = user_model.filter(age=30)
    assert len(results) == 1
    assert results[0].name == "John"


def test_model_all(user_model: type):
    user_model.create(name="John", age=30)
    user_model.create(name="Jane", age=25)

    results = user_model.all()
    assert len(results) == 2
