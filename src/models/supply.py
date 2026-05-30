from src.utils.enums import SupplyStatus
from src.utils.exceptions import InvalidStateError, ValidationError
from src.utils.validators import require_non_empty, require_positive


class SupplyItem:
    """Позиція у поставці: товар, кількість і закупівельна ціна."""

    def __init__(self, product_id, quantity, unit_cost):
        self.product_id = require_non_empty(product_id, "product_id")
        self.quantity = require_positive(quantity, "quantity")
        self.unit_cost = require_positive(unit_cost, "unit_cost")

    @property
    def total_cost(self):
        return self.quantity * self.unit_cost


class Supply:
    """Поставка від постачальника. Має життєвий цикл від чернетки до прийому."""

    def __init__(self, supply_id, supplier_id):
        self.id = require_non_empty(supply_id, "id")
        self.supplier_id = require_non_empty(supplier_id, "supplier_id")
        self.items = []
        self.status = SupplyStatus.DRAFT

    def add_item(self, item):
        if self.status != SupplyStatus.DRAFT:
            raise InvalidStateError("Додавати позиції можна лише у чернетку")
        if not isinstance(item, SupplyItem):
            raise ValidationError("Очікується обʼєкт SupplyItem")
        self.items.append(item)

    @property
    def total_cost(self):
        return sum(item.total_cost for item in self.items)

    @property
    def total_units(self):
        return sum(item.quantity for item in self.items)

    def confirm(self):
        if self.status != SupplyStatus.DRAFT:
            raise InvalidStateError("Підтвердити можна лише чернетку")
        if not self.items:
            raise InvalidStateError("Не можна підтвердити порожню поставку")
        self.status = SupplyStatus.CONFIRMED

    def mark_received(self):
        if self.status != SupplyStatus.CONFIRMED:
            raise InvalidStateError("Прийняти можна лише підтверджену поставку")
        self.status = SupplyStatus.RECEIVED

    def cancel(self):
        if self.status == SupplyStatus.RECEIVED:
            raise InvalidStateError("Прийняту поставку скасувати не можна")
        self.status = SupplyStatus.CANCELLED

    def __repr__(self):
        return "Supply(id={}, status={})".format(self.id, self.status.value)
