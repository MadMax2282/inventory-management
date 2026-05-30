from src.utils.enums import SaleStatus
from src.utils.exceptions import InvalidStateError, ValidationError
from src.utils.validators import require_non_empty, require_positive


class SaleItem:
    """Позиція продажу: товар, кількість, ціна за одиницю на момент продажу."""

    def __init__(self, product_id, quantity, unit_price):
        self.product_id = require_non_empty(product_id, "product_id")
        self.quantity = require_positive(quantity, "quantity")
        self.unit_price = require_positive(unit_price, "unit_price")

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class Sale:
    """Продаж товару клієнту. Сума рахується з позицій із врахуванням знижки."""

    def __init__(self, sale_id, seller_id, customer_id=None):
        self.id = require_non_empty(sale_id, "id")
        self.seller_id = require_non_empty(seller_id, "seller_id")
        self.customer_id = customer_id
        self.items = []
        self.status = SaleStatus.NEW
        self.discount = 0.0

    def add_item(self, item):
        if self.status != SaleStatus.NEW:
            raise InvalidStateError("Додавати позиції можна лише у новий продаж")
        if not isinstance(item, SaleItem):
            raise ValidationError("Очікується обʼєкт SaleItem")
        self.items.append(item)

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items)

    @property
    def total(self):
        return round(self.subtotal - self.discount, 2)

    @property
    def total_units(self):
        return sum(item.quantity for item in self.items)

    def apply_discount(self, amount):
        if amount < 0:
            raise ValidationError("Знижка не може бути відʼємною")
        if amount > self.subtotal:
            raise ValidationError("Знижка не може перевищувати суму продажу")
        self.discount = amount

    def complete(self):
        if self.status != SaleStatus.NEW:
            raise InvalidStateError("Завершити можна лише новий продаж")
        if not self.items:
            raise InvalidStateError("Не можна завершити порожній продаж")
        self.status = SaleStatus.COMPLETED

    def cancel(self):
        if self.status == SaleStatus.COMPLETED:
            raise InvalidStateError("Завершений продаж скасувати не можна")
        self.status = SaleStatus.CANCELLED

    def __repr__(self):
        return "Sale(id={}, total={})".format(self.id, self.total)
