from src.models.supplier import Supplier
from src.models.supply import Supply, SupplyItem
from src.utils.exceptions import InvalidStateError, ValidationError
from src.utils.id_generator import IdGenerator


class SupplyService:
    """Сервіс поставок. Реєструє постачальників і проводить прийом товару на склад."""

    def __init__(self, supply_repository, supplier_repository, inventory_service):
        self._supplies = supply_repository
        self._suppliers = supplier_repository
        self._inventory = inventory_service
        self._supply_ids = IdGenerator("SUP")
        self._supplier_ids = IdGenerator("SPL")

    def register_supplier(self, name, lead_time_days=1, rating=5.0):
        supplier = Supplier(self._supplier_ids.next_id(), name, lead_time_days, rating)
        self._suppliers.add(supplier)
        return supplier

    def create_supply(self, supplier_id):
        if not self._suppliers.exists(supplier_id):
            raise ValidationError("Постачальник {} не зареєстрований".format(supplier_id))
        supply = Supply(self._supply_ids.next_id(), supplier_id)
        self._supplies.add(supply)
        return supply

    def add_item(self, supply_id, product_id, quantity, unit_cost):
        supply = self._supplies.get(supply_id)
        # перевіряємо, що товар існує у системі
        self._inventory.get_product(product_id)
        supply.add_item(SupplyItem(product_id, quantity, unit_cost))
        self._supplies.update(supply)
        return supply

    def confirm_supply(self, supply_id):
        supply = self._supplies.get(supply_id)
        supply.confirm()
        self._supplies.update(supply)
        return supply

    def receive_supply(self, supply_id):
        supply = self._supplies.get(supply_id)
        supply.mark_received()
        for item in supply.items:
            self._inventory.receive_stock(item.product_id, item.quantity)
        self._supplies.update(supply)
        return supply

    def cancel_supply(self, supply_id):
        supply = self._supplies.get(supply_id)
        supply.cancel()
        self._supplies.update(supply)
        return supply

    def supplies_from(self, supplier_id):
        return self._supplies.get_by_supplier(supplier_id)
