import pytest

from src.services.inventory_service import InventoryService
from src.services.reservation_service import ReservationService
from src.storage.repositories import (
    MovementRepository,
    ProductRepository,
    ReservationRepository,
)
from src.utils.enums import CustomerTier, ReservationStatus
from src.utils.exceptions import InvalidStateError, ReservationError


@pytest.fixture
def inventory():
    service = InventoryService(ProductRepository(), MovementRepository())
    service.register_product("SKU-1", "Товар", 100.0, 10)
    return service


@pytest.fixture
def product_id(inventory):
    return inventory.list_products()[0].id


@pytest.fixture
def service(inventory):
    return ReservationService(ReservationRepository(), inventory)


def test_create_reservation(service, product_id):
    r = service.create_reservation(product_id, "client-1", 3)
    assert r.status == ReservationStatus.PENDING


def test_create_reservation_discontinued_raises(service, inventory, product_id):
    inventory.discontinue_product(product_id)
    with pytest.raises(ReservationError):
        service.create_reservation(product_id, "client-1", 3)


def test_allocate_single_reservation(service, inventory, product_id):
    r = service.create_reservation(product_id, "client-1", 4)
    allocated = service.allocate_pending(product_id)
    assert len(allocated) == 1
    assert r.status == ReservationStatus.ALLOCATED
    assert inventory.get_product(product_id).reserved_quantity == 4


def test_allocate_prefers_higher_tier(service, inventory, product_id):
    regular = service.create_reservation(product_id, "c1", 8, CustomerTier.REGULAR)
    vip = service.create_reservation(product_id, "c2", 8, CustomerTier.VIP)
    allocated = service.allocate_pending(product_id)
    # лише на одну заявку вистачить вільних 10 одиниць, має виграти VIP
    assert len(allocated) == 1
    assert allocated[0].id == vip.id
    assert regular.status == ReservationStatus.PENDING


def test_allocate_fifo_for_same_tier(service, inventory, product_id):
    first = service.create_reservation(product_id, "c1", 6, CustomerTier.GOLD)
    second = service.create_reservation(product_id, "c2", 6, CustomerTier.GOLD)
    allocated = service.allocate_pending(product_id)
    assert len(allocated) == 1
    assert allocated[0].id == first.id


def test_allocate_skips_oversized_then_fills_next(service, inventory, product_id):
    big = service.create_reservation(product_id, "c1", 20, CustomerTier.VIP)
    small = service.create_reservation(product_id, "c2", 5, CustomerTier.REGULAR)
    allocated = service.allocate_pending(product_id)
    # велика VIP-заявка не вміщається, тому виділяємо меншу
    assert len(allocated) == 1
    assert allocated[0].id == small.id
    assert big.status == ReservationStatus.PENDING


def test_allocate_multiple_when_enough_stock(service, inventory, product_id):
    service.create_reservation(product_id, "c1", 3)
    service.create_reservation(product_id, "c2", 4)
    allocated = service.allocate_pending(product_id)
    assert len(allocated) == 2
    assert inventory.get_product(product_id).reserved_quantity == 7


def test_fulfill_reservation(service, inventory, product_id):
    service.create_reservation(product_id, "c1", 4)
    service.allocate_pending(product_id)
    reservation = service.active_for_product(product_id)[0]
    service.fulfill_reservation(reservation.id)
    product = inventory.get_product(product_id)
    assert product.quantity_on_hand == 6
    assert product.reserved_quantity == 0


def test_fulfill_without_allocation_raises(service, product_id):
    r = service.create_reservation(product_id, "c1", 4)
    with pytest.raises(InvalidStateError):
        service.fulfill_reservation(r.id)


def test_cancel_allocated_releases_reserve(service, inventory, product_id):
    r = service.create_reservation(product_id, "c1", 4)
    service.allocate_pending(product_id)
    service.cancel_reservation(r.id)
    assert inventory.get_product(product_id).reserved_quantity == 0
    assert r.status == ReservationStatus.CANCELLED


def test_cancel_pending_keeps_stock(service, inventory, product_id):
    r = service.create_reservation(product_id, "c1", 4)
    service.cancel_reservation(r.id)
    assert inventory.get_product(product_id).reserved_quantity == 0
    assert r.status == ReservationStatus.CANCELLED


def test_expire_allocated_releases_reserve(service, inventory, product_id):
    r = service.create_reservation(product_id, "c1", 4)
    service.allocate_pending(product_id)
    service.expire_reservation(r.id)
    assert inventory.get_product(product_id).reserved_quantity == 0
    assert r.status == ReservationStatus.EXPIRED


def test_allocate_fires_notification(service, inventory, product_id):
    received = []
    observer_calls = []

    class Spy:
        def on_event(self, event, product, payload):
            observer_calls.append(event)
            if event == "reservation_allocated":
                received.append(payload.get("customer_id"))

    inventory.subject.attach(Spy())
    service.create_reservation(product_id, "client-1", 4)
    service.allocate_pending(product_id)
    assert "client-1" in received


def test_active_for_product(service, product_id):
    service.create_reservation(product_id, "c1", 2)
    service.create_reservation(product_id, "c2", 2)
    assert len(service.active_for_product(product_id)) == 2


def test_get_reservation(service, product_id):
    r = service.create_reservation(product_id, "c1", 2)
    assert service.get_reservation(r.id) is r


def test_available_drops_after_allocation(service, inventory, product_id):
    service.create_reservation(product_id, "c1", 4)
    service.allocate_pending(product_id)
    assert inventory.get_product(product_id).available_quantity == 6


def test_allocate_with_no_pending_returns_empty(service, product_id):
    assert service.allocate_pending(product_id) == []
