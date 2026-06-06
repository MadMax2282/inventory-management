import pytest

from src.application import Application
from src.patterns.discount_strategy import TierDiscount
from src.patterns.stock_observer import LowStockNotifier, ReorderLogger
from src.utils.enums import CustomerTier, WriteOffReason
from src.utils.exceptions import InsufficientStockError


@pytest.fixture
def app():
    return Application()


def _add_product(app, sku="SKU-1", price=100.0, qty=0, min_level=5, reorder=20):
    return app.inventory.register_product(sku, "Товар", price, qty, min_level, reorder)


def test_supply_increases_inventory(app):
    product = _add_product(app)
    supplier = app.supply.register_supplier("ТОВ Постач", 2, 4.0)
    supply = app.supply.create_supply(supplier.id)
    app.supply.add_item(supply.id, product.id, 100, 60.0)
    app.supply.confirm_supply(supply.id)
    app.supply.receive_supply(supply.id)
    assert app.inventory.get_product(product.id).quantity_on_hand == 100


def test_full_supply_then_sale_flow(app):
    product = _add_product(app, price=100.0)
    supplier = app.supply.register_supplier("Постач")
    supply = app.supply.create_supply(supplier.id)
    app.supply.add_item(supply.id, product.id, 50, 60.0)
    app.supply.confirm_supply(supply.id)
    app.supply.receive_supply(supply.id)

    sale = app.sales_service.create_sale("seller-1", "client-1")
    app.sales_service.add_item(sale.id, product.id, 10)
    completed = app.sales_service.complete_sale(sale.id)
    assert completed.total == 1000.0
    assert app.inventory.get_product(product.id).quantity_on_hand == 40


def test_sale_with_vip_discount(app):
    product = _add_product(app, price=100.0, qty=100)
    app.sales_service.set_discount_strategy(TierDiscount())
    sale = app.sales_service.create_sale("seller-1", "vip-1")
    app.sales_service.add_item(sale.id, product.id, 10)
    completed = app.sales_service.complete_sale(sale.id, CustomerTier.VIP)
    # 1000 мінус 12 відсотків
    assert completed.total == 880.0


def test_cannot_sell_more_than_stock(app):
    product = _add_product(app, qty=5)
    sale = app.sales_service.create_sale("seller-1")
    with pytest.raises(InsufficientStockError):
        app.sales_service.add_item(sale.id, product.id, 10)


def test_reservation_priority_across_clients(app):
    product = _add_product(app, qty=10)
    app.reservation.create_reservation(product.id, "regular", 8, CustomerTier.REGULAR)
    app.reservation.create_reservation(product.id, "vip", 6, CustomerTier.VIP)
    allocated = app.reservation.allocate_pending(product.id)
    # VIP отримує товар першим, на звичайного клієнта вже не вистачає
    assert len(allocated) == 1
    assert allocated[0].customer_id == "vip"


def test_reserved_stock_not_available_for_sale(app):
    product = _add_product(app, qty=10)
    app.reservation.create_reservation(product.id, "vip", 8, CustomerTier.VIP)
    app.reservation.allocate_pending(product.id)
    sale = app.sales_service.create_sale("seller-1")
    with pytest.raises(InsufficientStockError):
        app.sales_service.add_item(sale.id, product.id, 5)


def test_write_off_then_reorder_needed(app):
    product = _add_product(app, qty=8, min_level=5, reorder=20)
    app.write_off.write_off(product.id, 5, WriteOffReason.DAMAGED)
    plan = app.reorder.build_reorder_plan()
    assert len(plan) == 1
    assert plan[0]["product_id"] == product.id


def test_low_stock_notifier_fires_on_ship(app):
    notifier = LowStockNotifier()
    app.inventory.subject.attach(notifier)
    product = _add_product(app, qty=10, min_level=8)
    app.inventory.ship_stock(product.id, 5)
    assert len(notifier.messages) >= 1


def test_total_stock_value_after_supply(app):
    product = _add_product(app, price=25.0)
    supplier = app.supply.register_supplier("Постач")
    supply = app.supply.create_supply(supplier.id)
    app.supply.add_item(supply.id, product.id, 40, 15.0)
    app.supply.confirm_supply(supply.id)
    app.supply.receive_supply(supply.id)
    assert app.inventory.total_stock_value() == 1000.0


def test_cancelled_supply_does_not_change_stock(app):
    product = _add_product(app, qty=10)
    supplier = app.supply.register_supplier("Постач")
    supply = app.supply.create_supply(supplier.id)
    app.supply.add_item(supply.id, product.id, 50, 60.0)
    app.supply.cancel_supply(supply.id)
    assert app.inventory.get_product(product.id).quantity_on_hand == 10


def test_reservation_fulfillment_ships_goods(app):
    product = _add_product(app, qty=10)
    res = app.reservation.create_reservation(product.id, "vip", 6, CustomerTier.VIP)
    app.reservation.allocate_pending(product.id)
    app.reservation.fulfill_reservation(res.id)
    # після видачі резерву залишок зменшується
    assert app.inventory.get_product(product.id).quantity_on_hand == 4


def test_full_warehouse_cycle(app):
    # поставка, резерв, продаж, списання та перевірка перезамовлення разом
    logger = ReorderLogger()
    app.inventory.subject.attach(logger)
    product = _add_product(app, price=100.0, qty=0, min_level=10, reorder=30)
    supplier = app.supply.register_supplier("Головний постач", 3, 4.8)

    supply = app.supply.create_supply(supplier.id)
    app.supply.add_item(supply.id, product.id, 50, 60.0)
    app.supply.confirm_supply(supply.id)
    app.supply.receive_supply(supply.id)

    res = app.reservation.create_reservation(product.id, "vip", 10, CustomerTier.VIP)
    app.reservation.allocate_pending(product.id)
    app.reservation.fulfill_reservation(res.id)

    sale = app.sales_service.create_sale("seller-1", "client-1")
    app.sales_service.add_item(sale.id, product.id, 25)
    app.sales_service.complete_sale(sale.id)

    app.write_off.write_off(product.id, 8, WriteOffReason.DEFECT)

    remaining = app.inventory.get_product(product.id)
    assert remaining.quantity_on_hand == 7
    plan = app.reorder.build_reorder_plan()
    assert plan[0]["quantity"] == 30
    assert len(logger.entries) == 1
