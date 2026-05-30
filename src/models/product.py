from src.utils.enums import ProductStatus
from src.utils.exceptions import ValidationError
from src.utils.validators import (
    require_non_empty,
    require_non_negative,
    require_positive,
)


class Product:
    """Товар на складі. Зберігає залишок, резерв та параметри перезамовлення."""

    def __init__(
        self,
        product_id,
        sku,
        name,
        unit_price,
        quantity_on_hand=0,
        min_stock_level=0,
        reorder_quantity=0,
        category="general",
        status=ProductStatus.ACTIVE,
    ):
        self.id = require_non_empty(product_id, "id")
        self.sku = require_non_empty(sku, "sku")
        self.name = require_non_empty(name, "name")
        self.unit_price = require_positive(unit_price, "unit_price")
        self.quantity_on_hand = require_non_negative(quantity_on_hand, "quantity_on_hand")
        self.min_stock_level = require_non_negative(min_stock_level, "min_stock_level")
        self.reorder_quantity = require_non_negative(reorder_quantity, "reorder_quantity")
        self.category = category
        self.status = status
        self.reserved_quantity = 0

    @property
    def available_quantity(self):
        # доступно для продажу = весь залишок мінус те, що вже зарезервовано
        return self.quantity_on_hand - self.reserved_quantity

    @property
    def is_active(self):
        return self.status == ProductStatus.ACTIVE

    @property
    def needs_reorder(self):
        return self.available_quantity < self.min_stock_level

    def increase_stock(self, amount):
        if amount <= 0:
            raise ValidationError("Кількість для прибуття має бути додатною")
        self.quantity_on_hand += amount

    def decrease_stock(self, amount):
        if amount <= 0:
            raise ValidationError("Кількість для списання має бути додатною")
        if amount > self.quantity_on_hand:
            raise ValidationError("Не можна списати більше, ніж є на складі")
        self.quantity_on_hand -= amount

    def add_reservation(self, amount):
        if amount <= 0:
            raise ValidationError("Обсяг резерву має бути додатним")
        if amount > self.available_quantity:
            raise ValidationError("Недостатньо вільного товару для резерву")
        self.reserved_quantity += amount

    def release_reservation(self, amount):
        if amount <= 0:
            raise ValidationError("Обсяг зняття резерву має бути додатним")
        if amount > self.reserved_quantity:
            raise ValidationError("Не можна зняти більше резерву, ніж встановлено")
        self.reserved_quantity -= amount

    def discontinue(self):
        self.status = ProductStatus.DISCONTINUED

    def __repr__(self):
        return "Product(id={}, sku={}, qty={})".format(self.id, self.sku, self.quantity_on_hand)

    def __eq__(self, other):
        return isinstance(other, Product) and other.id == self.id

    def __hash__(self):
        return hash(self.id)
