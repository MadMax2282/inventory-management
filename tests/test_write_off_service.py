import pytest

from src.services.inventory_service import InventoryService
from src.services.write_off_service import WriteOffService
from src.storage.repositories import (
    MovementRepository,
    ProductRepository,
    WriteOffRepository,
)
from src.utils.enums import WriteOffReason
from src.utils.exceptions import InsufficientStockError


@pytest.fixture
def inventory():
    service = InventoryService(ProductRepository(), MovementRepository())
    service.register_product("SKU-1", "Товар", 50.0, 20)
    return service


@pytest.fixture
def product_id(inventory):
    return inventory.list_products()[0].id


@pytest.fixture
def service(inventory):
    return WriteOffService(WriteOffRepository(), inventory)


def test_write_off_reduces_stock(service, inventory, product_id):
    service.write_off(product_id, 5)
    assert inventory.get_product(product_id).quantity_on_hand == 15


def test_write_off_default_reason_is_defect(service, product_id):
    record = service.write_off(product_id, 2)
    assert record.reason == WriteOffReason.DEFECT


def test_defect_loss_is_full_value(service, product_id):
    record = service.write_off(product_id, 4, WriteOffReason.DEFECT)
    assert record.loss_amount == 200.0


def test_damaged_loss_uses_recovery_rate(service, product_id):
    # пошкоджений товар має 30 відсотків залишкової вартості
    record = service.write_off(product_id, 10, WriteOffReason.DAMAGED)
    assert record.loss_amount == 350.0


def test_expired_loss_is_full_value(service, product_id):
    record = service.write_off(product_id, 2, WriteOffReason.EXPIRED)
    assert record.loss_amount == 100.0


def test_lost_loss_is_full_value(service, product_id):
    record = service.write_off(product_id, 2, WriteOffReason.LOST)
    assert record.loss_amount == 100.0


def test_write_off_more_than_available_raises(service, product_id):
    with pytest.raises(InsufficientStockError):
        service.write_off(product_id, 100)


def test_cannot_write_off_reserved_part(service, inventory, product_id):
    inventory.reserve_stock(product_id, 15)
    # доступно лише 5, тож списання 10 неможливе
    with pytest.raises(InsufficientStockError):
        service.write_off(product_id, 10)


def test_total_loss_accumulates(service, product_id):
    service.write_off(product_id, 2, WriteOffReason.DEFECT)
    service.write_off(product_id, 2, WriteOffReason.DEFECT)
    assert service.total_loss() == 200.0


def test_total_loss_zero_initially(service):
    assert service.total_loss() == 0


def test_history_for_product(service, product_id):
    service.write_off(product_id, 1)
    service.write_off(product_id, 1)
    assert len(service.history_for(product_id)) == 2


def test_write_off_creates_record_with_id(service, product_id):
    record = service.write_off(product_id, 1)
    assert record.id.startswith("WRF-")


def test_write_off_logs_movement(service, inventory, product_id):
    before = len(inventory.movements_for(product_id))
    service.write_off(product_id, 1)
    after = len(inventory.movements_for(product_id))
    assert after == before + 1
