"""Custom exceptions for LightDB."""


class Error(Exception):
    """Base class for all LightDB errors."""


class ValidationError(Error, TypeError):
    """Raised when a field value fails type validation."""


class FieldNotFoundError(Error, ValueError):
    """Raised when a referenced field does not exist in the table."""


class NoArgsProvidedError(Error, TypeError):
    """Raised when a method that requires at least one argument is called with none."""
