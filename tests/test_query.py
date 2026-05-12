import pytest
import os

from lightdb.core import LightDB
from lightdb.query import Query, Condition, FieldProxy
from lightdb.fields import Field
from lightdb.models import Model
from lightdb.pk import int_pk


@pytest.fixture
def user_model():
    test_db_location = "test_db.json"
    LightDB(test_db_location)

    class User(Model, table="users", pk="id"):
        id: int = int_pk()
        name: str
        age: int
        items: list[str] = []
        extra: dict[str, object] = {}

    yield User

    if os.path.exists(test_db_location):
        os.remove(test_db_location)


def test_query_initialization(user_model: type):
    query = Query(user_model)
    assert query.model == user_model
    assert query.conditions == []


def test_query_where(user_model: type):
    query = Query(user_model)
    query.where(name="John", age=30)
    assert len(query.conditions) == 2
    names = {c.field.name for c in query.conditions}
    assert "name" in names
    assert "age" in names


def test_query_execute(user_model: type):
    user_model.create(name="John", age=30)
    user_model.create(name="Jane", age=25)

    query = Query(user_model)
    query.where(age=30)
    results = query.execute()

    assert len(results) == 1
    assert results[0].name == "John"


def test_condition_evaluate():
    proxy = FieldProxy(name="age")
    condition = Condition(proxy, "==", 30)

    class TestModelMock:
        age = 30

    model = TestModelMock()
    assert condition.evaluate(model) is True


def test_field_proxy_operators():
    proxy = FieldProxy("age")
    assert isinstance(proxy == 5, Condition)
    assert isinstance(proxy != 5, Condition)
    assert isinstance(proxy > 5, Condition)
    assert isinstance(proxy >= 5, Condition)
    assert isinstance(proxy < 5, Condition)
    assert isinstance(proxy <= 5, Condition)
