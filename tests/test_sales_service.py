import pytest

from src.patterns.discount_strategy import BulkDiscount, TierDiscount
from src.services.inventory_service import InventoryService
from src.services.sales_service import SalesService
from src.storage.repositories import (
    MovementRepository,
    ProductRepository,
    SaleRepository,
)
from src.utils.enums import CustomerTier
from src.utils.exceptions import (
    InsufficientStockError,
    InvalidStateError,
)


@pytest.fixture
def inventory():
    service = InventoryService(ProductRepository(), MovementRepository())
    service.register_product("SKU-1", "Товар", 100.0, 50)
    return service


@pytest.fixture
def product_id(inventory):
    return inventory.list_products()[0].id


@pytest.fixture
def service(inventory):
    return SalesService(SaleRepository(), inventory)


def test_create_sale(service):
    sale = service.create_sale("seller-1", "client-1")
    assert sale.seller_id == "seller-1"


def test_add_item(service, product_id):
    sale = service.create_sale("seller-1")
    service.add_item(sale.id, product_id, 3)
    assert sale.items[0].quantity == 3


def test_add_item_insufficient_stock_raises(service, product_id):
    sale = service.create_sale("seller-1")
    with pytest.raises(InsufficientStockError):
        service.add_item(sale.id, product_id, 100)


def test_add_item_discontinued_raises(service, inventory, product_id):
    inventory.discontinue_product(product_id)
    sale = service.create_sale("seller-1")
    with pytest.raises(InvalidStateError):
        service.add_item(sale.id, product_id, 1)


def test_complete_sale_reduces_stock(service, inventory, product_id):
    sale = service.create_sale("seller-1")
    service.add_item(sale.id, product_id, 5)
    service.complete_sale(sale.id)
    assert inventory.get_product(product_id).quantity_on_hand == 45


def test_complete_sale_sets_status(service, product_id):
    sale = service.create_sale("seller-1")
    service.add_item(sale.id, product_id, 2)
    service.complete_sale(sale.id)
    assert sale.status.value == "completed"


def test_complete_sale_applies_tier_discount(inventory, product_id):
    service = SalesService(SaleRepository(), inventory, TierDiscount())
    sale = service.create_sale("seller-1", "client-1")
    service.add_item(sale.id, product_id, 2)
    service.complete_sale(sale.id, CustomerTier.VIP)
    # 2*100=200, знижка vip 12% = 24
    assert sale.discount == 24.0
    assert sale.total == 176.0


def test_complete_sale_applies_bulk_discount(inventory, product_id):
    service = SalesService(SaleRepository(), inventory, BulkDiscount(threshold=100,
                                                                     rate=0.1))
    sale = service.create_sale("seller-1")
    service.add_item(sale.id, product_id, 5)
    service.complete_sale(sale.id)
    assert sale.discount == 50.0


def test_set_discount_strategy(service, product_id):
    service.set_discount_strategy(TierDiscount())
    sale = service.create_sale("seller-1")
    service.add_item(sale.id, product_id, 1)
    service.complete_sale(sale.id, CustomerTier.GOLD)
    assert sale.discount == 7.0


def test_cancel_sale(service):
    sale = service.create_sale("seller-1")
    service.cancel_sale(sale.id)
    assert sale.status.value == "cancelled"


def test_get_sale(service):
    sale = service.create_sale("seller-1")
    assert service.get_sale(sale.id) is sale


def test_complete_sale_records_movement(service, inventory, product_id):
    sale = service.create_sale("seller-1")
    service.add_item(sale.id, product_id, 3)
    service.complete_sale(sale.id)
    assert len(inventory.movements_for(product_id)) == 1


def test_two_sales_reduce_stock_independently(service, inventory, product_id):
    first = service.create_sale("seller-1")
    service.add_item(first.id, product_id, 10)
    service.complete_sale(first.id)
    second = service.create_sale("seller-2")
    service.add_item(second.id, product_id, 5)
    service.complete_sale(second.id)
    assert inventory.get_product(product_id).quantity_on_hand == 35
