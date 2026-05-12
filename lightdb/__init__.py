"""
LightDB
~~~~~~~

A lightweight JSON-backed database for Python 3.12+.

Modules:
    core: Main LightDB implementation
    exceptions: Custom exceptions
    fields: Field class for type validation (legacy)
    models: Model base class
    pk: Primary key helpers
    query: Query and Condition classes
"""

from .core import LightDB
from .fields import Field
from .models import Model
from .pk import int_pk, uuid_pk
from .query import Condition, FieldProxy, Query

__all__ = ["LightDB", "Field", "Model", "Query", "Condition", "FieldProxy", "int_pk", "uuid_pk"]
__version__ = "3.0.0"
