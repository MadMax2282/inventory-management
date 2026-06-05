import pytest

from src.models.reservation import Reservation
from src.models.write_off import StockMovement, WriteOff
from src.utils.enums import (
    CustomerTier,
    MovementType,
    ReservationStatus,
    WriteOffReason,
)
from src.utils.exceptions import InvalidStateError, ValidationError


def test_reservation_creation():
    r = Reservation("RES-1", "PRD-1", "client-1", 5, CustomerTier.GOLD, 1)
    assert r.status == ReservationStatus.PENDING
    assert r.quantity == 5
    assert r.tier == CustomerTier.GOLD


def test_reservation_zero_quantity_raises():
    with pytest.raises(ValidationError):
        Reservation("RES-1", "PRD-1", "client-1", 0)


def test_reservation_priority_value_vip():
    r = Reservation("RES-1", "PRD-1", "client-1", 5, CustomerTier.VIP)
    assert r.priority_value == 4


def test_reservation_priority_value_regular():
    r = Reservation("RES-1", "PRD-1", "client-1", 5, CustomerTier.REGULAR)
    assert r.priority_value == 1


def test_reservation_allocate():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.allocate()
    assert r.status == ReservationStatus.ALLOCATED


def test_reservation_allocate_twice_raises():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.allocate()
    with pytest.raises(InvalidStateError):
        r.allocate()


def test_reservation_fulfill():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.allocate()
    r.fulfill()
    assert r.status == ReservationStatus.FULFILLED


def test_reservation_fulfill_without_allocate_raises():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    with pytest.raises(InvalidStateError):
        r.fulfill()


def test_reservation_cancel():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.cancel()
    assert r.status == ReservationStatus.CANCELLED


def test_reservation_cancel_fulfilled_raises():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.allocate()
    r.fulfill()
    with pytest.raises(InvalidStateError):
        r.cancel()


def test_reservation_expire():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.expire()
    assert r.status == ReservationStatus.EXPIRED


def test_reservation_expire_cancelled_raises():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.cancel()
    with pytest.raises(InvalidStateError):
        r.expire()


def test_reservation_is_active_pending():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    assert r.is_active is True


def test_reservation_is_active_allocated():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.allocate()
    assert r.is_active is True


def test_reservation_not_active_after_cancel():
    r = Reservation("RES-1", "PRD-1", "client-1", 5)
    r.cancel()
    assert r.is_active is False


def test_reservation_repr():
    r = Reservation("RES-9", "PRD-1", "client-1", 5)
    assert "RES-9" in repr(r)


def test_write_off_creation():
    w = WriteOff("WRF-1", "PRD-1", 3, WriteOffReason.DAMAGED)
    assert w.quantity == 3
    assert w.reason == WriteOffReason.DAMAGED
    assert w.loss_amount == 0.0


def test_write_off_zero_quantity_raises():
    with pytest.raises(ValidationError):
        WriteOff("WRF-1", "PRD-1", 0)


def test_write_off_set_loss_rounds():
    w = WriteOff("WRF-1", "PRD-1", 3)
    w.set_loss(99.999)
    assert w.loss_amount == 100.0


def test_write_off_repr():
    w = WriteOff("WRF-2", "PRD-1", 3)
    assert "WRF-2" in repr(w)


def test_stock_movement_inbound_flag():
    m = StockMovement("MOV-1", "PRD-1", MovementType.INBOUND, 10)
    assert m.is_inbound is True


def test_stock_movement_outbound_not_inbound():
    m = StockMovement("MOV-1", "PRD-1", MovementType.OUTBOUND, -10)
    assert m.is_inbound is False


def test_stock_movement_repr():
    m = StockMovement("MOV-1", "PRD-5", MovementType.RESERVE, 4)
    assert "PRD-5" in repr(m)
