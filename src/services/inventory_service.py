from src.models.product import Product
from src.patterns.movement_factory import MovementFactory
from src.patterns.stock_observer import StockSubject
from src.utils.enums import ProductStatus
from src.utils.exceptions import InsufficientStockError, ValidationError
from src.utils.id_generator import IdGenerator


class InventoryService:
    """Сервіс залишків. Єдина точка зміни кількості товару та джерело подій."""

    def __init__(self, product_repository, movement_repository):
        self._products = product_repository
        self._movements = movement_repository
        self._product_ids = IdGenerator("PRD")
        self._factory = MovementFactory(IdGenerator("MOV"))
        self.subject = StockSubject()

    def register_product(self, sku, name, unit_price, quantity_on_hand=0,
                         min_stock_level=0, reorder_quantity=0, category="general"):
        if self._products.get_by_sku(sku) is not None:
            raise ValidationError("Товар з артикулом {} вже існує".format(sku))
        product = Product(
            self._product_ids.next_id(),
            sku,
            name,
            unit_price,
            quantity_on_hand,
            min_stock_level,
            reorder_quantity,
            category,
        )
        self._products.add(product)
        return product

    def get_product(self, product_id):
        return self._products.get(product_id)

    def list_products(self):
        return self._products.get_all()

    def receive_stock(self, product_id, quantity):
        product = self._products.get(product_id)
        product.increase_stock(quantity)
        self._products.update(product)
        self._movements.add(self._factory.inbound(product_id, quantity))
        return product

    def ship_stock(self, product_id, quantity):
        product = self._products.get(product_id)
        if quantity > product.available_quantity:
            raise InsufficientStockError(
                "Недостатньо доступного товару {} для відвантаження".format(product.sku)
            )
        product.decrease_stock(quantity)
        self._products.update(product)
        self._movements.add(self._factory.outbound(product_id, quantity))
        self._check_low_stock(product)
        return product

    def adjust_stock(self, product_id, delta):
        product = self._products.get(product_id)
        new_value = product.quantity_on_hand + delta
        if new_value < product.reserved_quantity:
            raise ValidationError("Коригування суперечить наявному резерву")
        if new_value < 0:
            raise ValidationError("Залишок не може стати відʼємним")
        product.quantity_on_hand = new_value
        self._products.update(product)
        self._movements.add(self._factory.adjustment(product_id, delta))
        self._check_low_stock(product)
        return product

    def reserve_stock(self, product_id, quantity):
        product = self._products.get(product_id)
        product.add_reservation(quantity)
        self._products.update(product)
        self._movements.add(self._factory.reserve(product_id, quantity))
        return product

    def release_stock(self, product_id, quantity):
        product = self._products.get(product_id)
        product.release_reservation(quantity)
        self._products.update(product)
        self._movements.add(self._factory.release(product_id, quantity))
        return product

    def fulfill_reserved(self, product_id, quantity):
        product = self._products.get(product_id)
        product.release_reservation(quantity)
        product.decrease_stock(quantity)
        self._products.update(product)
        self._movements.add(self._factory.outbound(product_id, quantity))
        self._check_low_stock(product)
        return product

    def discontinue_product(self, product_id):
        product = self._products.get(product_id)
        if product.reserved_quantity > 0:
            raise ValidationError("Не можна зняти з продажу товар з активним резервом")
        product.discontinue()
        self._products.update(product)
        return product

    def movements_for(self, product_id):
        return self._movements.get_for_product(product_id)

    def _check_low_stock(self, product):
        if product.is_active and product.needs_reorder:
            self.subject.notify("low_stock", product)

    def total_stock_value(self):
        active = [p for p in self._products.get_all() if p.status == ProductStatus.ACTIVE]
        return round(sum(p.quantity_on_hand * p.unit_price for p in active), 2)
