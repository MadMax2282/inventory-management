import pytest

from src.models.sale import Sale, SaleItem
from src.utils.enums import SaleStatus
from src.utils.exceptions import InvalidStateError, ValidationError


def test_sale_item_line_total():
    item = SaleItem("PRD-1", 4, 25.0)
    assert item.line_total == 100.0


def test_sale_item_zero_price_raises():
    with pytest.raises(ValidationError):
        SaleItem("PRD-1", 4, 0)


def test_sale_starts_new():
    s = Sale("SAL-1", "seller-1")
    assert s.status == SaleStatus.NEW
    assert s.discount == 0.0


def test_sale_add_item():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 2, 50.0))
    assert len(s.items) == 1


def test_sale_add_wrong_type_raises():
    s = Sale("SAL-1", "seller-1")
    with pytest.raises(ValidationError):
        s.add_item("bad")


def test_sale_subtotal():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 2, 50.0))
    s.add_item(SaleItem("PRD-2", 1, 30.0))
    assert s.subtotal == 130.0


def test_sale_total_units():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 2, 50.0))
    s.add_item(SaleItem("PRD-2", 3, 30.0))
    assert s.total_units == 5


def test_sale_apply_discount():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 2, 50.0))
    s.apply_discount(20)
    assert s.total == 80.0


def test_sale_discount_negative_raises():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 2, 50.0))
    with pytest.raises(ValidationError):
        s.apply_discount(-5)


def test_sale_discount_over_subtotal_raises():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 2, 50.0))
    with pytest.raises(ValidationError):
        s.apply_discount(200)


def test_sale_complete():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 1, 50.0))
    s.complete()
    assert s.status == SaleStatus.COMPLETED


def test_sale_complete_empty_raises():
    s = Sale("SAL-1", "seller-1")
    with pytest.raises(InvalidStateError):
        s.complete()


def test_sale_add_item_after_complete_raises():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 1, 50.0))
    s.complete()
    with pytest.raises(InvalidStateError):
        s.add_item(SaleItem("PRD-2", 1, 50.0))


def test_sale_cancel():
    s = Sale("SAL-1", "seller-1")
    s.cancel()
    assert s.status == SaleStatus.CANCELLED


def test_sale_cancel_completed_raises():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 1, 50.0))
    s.complete()
    with pytest.raises(InvalidStateError):
        s.cancel()


def test_sale_total_rounds():
    s = Sale("SAL-1", "seller-1")
    s.add_item(SaleItem("PRD-1", 3, 10.10))
    s.apply_discount(0.005)
    assert s.total == 30.29 or s.total == 30.3


def test_sale_with_customer():
    s = Sale("SAL-1", "seller-1", "client-9")
    assert s.customer_id == "client-9"


def test_sale_repr_contains_id():
    s = Sale("SAL-7", "seller-1")
    assert "SAL-7" in repr(s)
