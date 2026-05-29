class InventoryError(Exception):
    """Базовий виняток системи складу."""


class EntityNotFoundError(InventoryError):
    """Сутність не знайдено у сховищі."""


class DuplicateEntityError(InventoryError):
    """Сутність з таким ідентифікатором вже існує."""


class ValidationError(InventoryError):
    """Некоректні вхідні дані."""


class InsufficientStockError(InventoryError):
    """Недостатньо товару на складі для операції."""


class InvalidStateError(InventoryError):
    """Операція недопустима у поточному стані сутності."""


class ReservationError(InventoryError):
    """Помилка під час роботи з резервуванням."""
