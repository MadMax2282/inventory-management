from unittest.mock import MagicMock

import pytest

from src.services.inventory_service import InventoryService
from src.services.supply_service import SupplyService
from src.storage.repositories import (
    MovementRepository,
    ProductRepository,
    SupplierRepository,
    SupplyRepository,
)
from src.utils.exceptions import (
    EntityNotFoundError,
    InvalidStateError,
    ValidationError,
)


@pytest.fixture
def inventory():
    return InventoryService(ProductRepository(), MovementRepository())


@pytest.fixture
def service(inventory):
    return SupplyService(SupplyRepository(), SupplierRepository(), inventory)


def test_register_supplier(service):
    supplier = service.register_supplier("Постачальник", 3)
    assert supplier.id.startswith("SPL-")


def test_create_supply(service):
    supplier = service.register_supplier("Постачальник")
    supply = service.create_supply(supplier.id)
    assert supply.supplier_id == supplier.id


def test_create_supply_unknown_supplier_raises(service):
    with pytest.raises(ValidationError):
        service.create_supply("SPL-999")


def test_add_item(service, inventory):
    supplier = service.register_supplier("Постачальник")
    product = inventory.register_product("SKU-1", "Товар", 10.0)
    supply = service.create_supply(supplier.id)
    service.add_item(supply.id, product.id, 10, 8.0)
    assert len(supply.items) == 1


def test_add_item_unknown_product_raises(service):
    supplier = service.register_supplier("Постачальник")
    supply = service.create_supply(supplier.id)
    with pytest.raises(EntityNotFoundError):
        service.add_item(supply.id, "PRD-999", 5, 8.0)


def test_confirm_supply(service, inventory):
    supplier = service.register_supplier("Постачальник")
    product = inventory.register_product("SKU-1", "Товар", 10.0)
    supply = service.create_supply(supplier.id)
    service.add_item(supply.id, product.id, 10, 8.0)
    service.confirm_supply(supply.id)
    assert supply.status.value == "confirmed"


def test_receive_supply_updates_stock(service, inventory):
    supplier = service.register_supplier("Постачальник")
    product = inventory.register_product("SKU-1", "Товар", 10.0, 0)
    supply = service.create_supply(supplier.id)
    service.add_item(supply.id, product.id, 25, 8.0)
    service.confirm_supply(supply.id)
    service.receive_supply(supply.id)
    assert inventory.get_product(product.id).quantity_on_hand == 25


def test_receive_supply_multiple_items(service, inventory):
    supplier = service.register_supplier("Постачальник")
    p1 = inventory.register_product("SKU-1", "А", 10.0)
    p2 = inventory.register_product("SKU-2", "Б", 20.0)
    supply = service.create_supply(supplier.id)
    service.add_item(supply.id, p1.id, 10, 5.0)
    service.add_item(supply.id, p2.id, 7, 12.0)
    service.confirm_supply(supply.id)
    service.receive_supply(supply.id)
    assert inventory.get_product(p1.id).quantity_on_hand == 10
    assert inventory.get_product(p2.id).quantity_on_hand == 7


def test_receive_without_confirm_raises(service, inventory):
    supplier = service.register_supplier("Постачальник")
    product = inventory.register_product("SKU-1", "Товар", 10.0)
    supply = service.create_supply(supplier.id)
    service.add_item(supply.id, product.id, 5, 8.0)
    with pytest.raises(InvalidStateError):
        service.receive_supply(supply.id)


def test_cancel_supply(service):
    supplier = service.register_supplier("Постачальник")
    supply = service.create_supply(supplier.id)
    service.cancel_supply(supply.id)
    assert supply.status.value == "cancelled"


def test_supplies_from_supplier(service):
    supplier = service.register_supplier("Постачальник")
    service.create_supply(supplier.id)
    service.create_supply(supplier.id)
    assert len(service.supplies_from(supplier.id)) == 2


def test_supply_service_with_mock_inventory():
    supplies = SupplyRepository()
    suppliers = SupplierRepository()
    inventory = MagicMock()
    service = SupplyService(supplies, suppliers, inventory)
    supplier = service.register_supplier("Постачальник")
    supply = service.create_supply(supplier.id)
    service.add_item(supply.id, "PRD-1", 5, 8.0)
    inventory.get_product.assert_called_with("PRD-1")


def test_receive_supply_calls_inventory_receive():
    supplies = SupplyRepository()
    suppliers = SupplierRepository()
    inventory = MagicMock()
    service = SupplyService(supplies, suppliers, inventory)
    supplier = service.register_supplier("Постачальник")
    supply = service.create_supply(supplier.id)
    service.add_item(supply.id, "PRD-1", 5, 8.0)
    service.confirm_supply(supply.id)
    service.receive_supply(supply.id)
    inventory.receive_stock.assert_called_once_with("PRD-1", 5)
