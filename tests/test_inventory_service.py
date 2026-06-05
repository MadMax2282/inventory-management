from unittest.mock import MagicMock

import pytest

from src.services.inventory_service import InventoryService
from src.storage.repositories import MovementRepository, ProductRepository
from src.utils.exceptions import (
    EntityNotFoundError,
    InsufficientStockError,
    ValidationError,
)


@pytest.fixture
def service():
    return InventoryService(ProductRepository(), MovementRepository())


def test_register_product(service):
    p = service.register_product("SKU-1", "Товар", 100.0, 10, 5, 20)
    assert p.id.startswith("PRD-")
    assert service.get_product(p.id) is p


def test_register_duplicate_sku_raises(service):
    service.register_product("SKU-1", "Товар", 100.0)
    with pytest.raises(ValidationError):
        service.register_product("SKU-1", "Інший", 50.0)


def test_get_missing_product_raises(service):
    with pytest.raises(EntityNotFoundError):
        service.get_product("PRD-999")


def test_list_products(service):
    service.register_product("SKU-1", "А", 10.0)
    service.register_product("SKU-2", "Б", 20.0)
    assert len(service.list_products()) == 2


def test_receive_stock_increases_quantity(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 5)
    service.receive_stock(p.id, 10)
    assert service.get_product(p.id).quantity_on_hand == 15


def test_receive_stock_records_movement(service):
    p = service.register_product("SKU-1", "Товар", 10.0)
    service.receive_stock(p.id, 10)
    assert len(service.movements_for(p.id)) == 1


def test_ship_stock_decreases_quantity(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 20)
    service.ship_stock(p.id, 5)
    assert service.get_product(p.id).quantity_on_hand == 15


def test_ship_more_than_available_raises(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 5)
    with pytest.raises(InsufficientStockError):
        service.ship_stock(p.id, 10)


def test_ship_respects_reserved(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 10)
    service.reserve_stock(p.id, 8)
    with pytest.raises(InsufficientStockError):
        service.ship_stock(p.id, 5)


def test_adjust_stock_positive(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 10)
    service.adjust_stock(p.id, 5)
    assert service.get_product(p.id).quantity_on_hand == 15


def test_adjust_stock_negative(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 10)
    service.adjust_stock(p.id, -4)
    assert service.get_product(p.id).quantity_on_hand == 6


def test_adjust_below_zero_raises(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 5)
    with pytest.raises(ValidationError):
        service.adjust_stock(p.id, -10)


def test_adjust_conflicts_with_reserve_raises(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 10)
    service.reserve_stock(p.id, 8)
    with pytest.raises(ValidationError):
        service.adjust_stock(p.id, -5)


def test_reserve_stock(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 10)
    service.reserve_stock(p.id, 4)
    assert service.get_product(p.id).reserved_quantity == 4


def test_release_stock(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 10)
    service.reserve_stock(p.id, 4)
    service.release_stock(p.id, 2)
    assert service.get_product(p.id).reserved_quantity == 2


def test_fulfill_reserved_reduces_on_hand_and_reserve(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 10)
    service.reserve_stock(p.id, 4)
    service.fulfill_reserved(p.id, 4)
    product = service.get_product(p.id)
    assert product.quantity_on_hand == 6
    assert product.reserved_quantity == 0


def test_discontinue_product(service):
    p = service.register_product("SKU-1", "Товар", 10.0)
    service.discontinue_product(p.id)
    assert service.get_product(p.id).is_active is False


def test_discontinue_with_reserve_raises(service):
    p = service.register_product("SKU-1", "Товар", 10.0, 10)
    service.reserve_stock(p.id, 3)
    with pytest.raises(ValidationError):
        service.discontinue_product(p.id)


def test_total_stock_value(service):
    service.register_product("SKU-1", "А", 10.0, 5)
    service.register_product("SKU-2", "Б", 20.0, 2)
    assert service.total_stock_value() == 90.0


def test_low_stock_event_fired_on_ship(service):
    notifications = []
    observer = MagicMock()
    observer.on_event = lambda event, product, payload: notifications.append(event)
    service.subject.attach(observer)
    p = service.register_product("SKU-1", "Товар", 10.0, 12, 10)
    service.ship_stock(p.id, 5)
    assert "low_stock" in notifications


def test_ship_uses_repository_update():
    # ізолюємо сервіс від реального сховища через mock
    products = MagicMock()
    movements = MagicMock()
    product = MagicMock()
    product.available_quantity = 10
    product.is_active = True
    product.needs_reorder = False
    products.get.return_value = product
    service = InventoryService(products, movements)
    service.ship_stock("PRD-1", 3)
    product.decrease_stock.assert_called_once_with(3)
    products.update.assert_called_once()


def test_receive_stock_uses_mock_repository():
    products = MagicMock()
    movements = MagicMock()
    product = MagicMock()
    products.get.return_value = product
    service = InventoryService(products, movements)
    service.receive_stock("PRD-1", 7)
    product.increase_stock.assert_called_once_with(7)
    movements.add.assert_called_once()
