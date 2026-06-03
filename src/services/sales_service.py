from src.models.sale import Sale, SaleItem
from src.patterns.discount_strategy import NoDiscount
from src.utils.enums import CustomerTier
from src.utils.exceptions import InsufficientStockError, InvalidStateError
from src.utils.id_generator import IdGenerator


class SalesService:
    """Сервіс продажів. Перевіряє наявність, рахує знижку та списує товар при завершенні."""

    def __init__(self, sale_repository, inventory_service, discount_strategy=None):
        self._sales = sale_repository
        self._inventory = inventory_service
        self._discount_strategy = discount_strategy or NoDiscount()
        self._sale_ids = IdGenerator("SAL")

    def set_discount_strategy(self, strategy):
        self._discount_strategy = strategy

    def create_sale(self, seller_id, customer_id=None):
        sale = Sale(self._sale_ids.next_id(), seller_id, customer_id)
        self._sales.add(sale)
        return sale

    def add_item(self, sale_id, product_id, quantity):
        sale = self._sales.get(sale_id)
        product = self._inventory.get_product(product_id)
        if not product.is_active:
            raise InvalidStateError("Товар {} знято з продажу".format(product.sku))
        if quantity > product.available_quantity:
            raise InsufficientStockError(
                "Недостатньо товару {} для продажу".format(product.sku)
            )
        sale.add_item(SaleItem(product_id, quantity, product.unit_price))
        self._sales.update(sale)
        return sale

    def complete_sale(self, sale_id, customer_tier=CustomerTier.REGULAR):
        sale = self._sales.get(sale_id)
        discount = self._discount_strategy.calculate(sale.subtotal, customer_tier)
        sale.apply_discount(discount)
        # повторно перевіряємо наявність перед фактичним списанням
        for item in sale.items:
            product = self._inventory.get_product(item.product_id)
            if item.quantity > product.available_quantity:
                raise InsufficientStockError(
                    "Залишку товару {} не вистачає на момент завершення".format(product.sku)
                )
        for item in sale.items:
            self._inventory.ship_stock(item.product_id, item.quantity)
        sale.complete()
        self._sales.update(sale)
        return sale

    def cancel_sale(self, sale_id):
        sale = self._sales.get(sale_id)
        sale.cancel()
        self._sales.update(sale)
        return sale

    def get_sale(self, sale_id):
        return self._sales.get(sale_id)
