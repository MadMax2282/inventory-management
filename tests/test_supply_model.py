import pytest

from src.models.supply import Supply, SupplyItem
from src.utils.enums import SupplyStatus
from src.utils.exceptions import InvalidStateError, ValidationError


def test_supply_item_total_cost():
    item = SupplyItem("PRD-1", 10, 5.0)
    assert item.total_cost == 50.0


def test_supply_item_zero_quantity_raises():
    with pytest.raises(ValidationError):
        SupplyItem("PRD-1", 0, 5.0)


def test_supply_item_negative_cost_raises():
    with pytest.raises(ValidationError):
        SupplyItem("PRD-1", 5, -1)


def test_supply_starts_as_draft():
    s = Supply("SUP-1", "SPL-1")
    assert s.status == SupplyStatus.DRAFT
    assert s.items == []


def test_supply_add_item():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 3, 10.0))
    assert len(s.items) == 1


def test_supply_add_wrong_type_raises():
    s = Supply("SUP-1", "SPL-1")
    with pytest.raises(ValidationError):
        s.add_item("not an item")


def test_supply_total_cost():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 2, 10.0))
    s.add_item(SupplyItem("PRD-2", 3, 20.0))
    assert s.total_cost == 80.0


def test_supply_total_units():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 2, 10.0))
    s.add_item(SupplyItem("PRD-2", 3, 20.0))
    assert s.total_units == 5


def test_supply_confirm():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 1, 10.0))
    s.confirm()
    assert s.status == SupplyStatus.CONFIRMED


def test_supply_confirm_empty_raises():
    s = Supply("SUP-1", "SPL-1")
    with pytest.raises(InvalidStateError):
        s.confirm()


def test_supply_add_item_after_confirm_raises():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 1, 10.0))
    s.confirm()
    with pytest.raises(InvalidStateError):
        s.add_item(SupplyItem("PRD-2", 1, 10.0))


def test_supply_receive():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 1, 10.0))
    s.confirm()
    s.mark_received()
    assert s.status == SupplyStatus.RECEIVED


def test_supply_receive_without_confirm_raises():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 1, 10.0))
    with pytest.raises(InvalidStateError):
        s.mark_received()


def test_supply_cancel_draft():
    s = Supply("SUP-1", "SPL-1")
    s.cancel()
    assert s.status == SupplyStatus.CANCELLED


def test_supply_cancel_received_raises():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 1, 10.0))
    s.confirm()
    s.mark_received()
    with pytest.raises(InvalidStateError):
        s.cancel()


def test_supply_confirm_twice_raises():
    s = Supply("SUP-1", "SPL-1")
    s.add_item(SupplyItem("PRD-1", 1, 10.0))
    s.confirm()
    with pytest.raises(InvalidStateError):
        s.confirm()


def test_supply_repr_contains_status():
    s = Supply("SUP-9", "SPL-1")
    assert "draft" in repr(s)
