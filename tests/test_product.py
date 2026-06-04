import pytest

from src.models.product import Product
from src.utils.enums import ProductStatus
from src.utils.exceptions import ValidationError


def test_product_creation_sets_fields():
    p = Product("PRD-1", "SKU-1", "Товар", 100.0, 30, 5, 10)
    assert p.id == "PRD-1"
    assert p.sku == "SKU-1"
    assert p.name == "Товар"
    assert p.unit_price == 100.0
    assert p.quantity_on_hand == 30


def test_product_default_values():
    p = Product("PRD-2", "SKU-2", "Товар", 10.0)
    assert p.quantity_on_hand == 0
    assert p.min_stock_level == 0
    assert p.reorder_quantity == 0
    assert p.category == "general"
    assert p.status == ProductStatus.ACTIVE
    assert p.reserved_quantity == 0


def test_product_empty_id_raises():
    with pytest.raises(ValidationError):
        Product("", "SKU", "Товар", 10.0)


def test_product_empty_sku_raises():
    with pytest.raises(ValidationError):
        Product("PRD-1", "", "Товар", 10.0)


def test_product_empty_name_raises():
    with pytest.raises(ValidationError):
        Product("PRD-1", "SKU", "", 10.0)


def test_product_zero_price_raises():
    with pytest.raises(ValidationError):
        Product("PRD-1", "SKU", "Товар", 0)


def test_product_negative_price_raises():
    with pytest.raises(ValidationError):
        Product("PRD-1", "SKU", "Товар", -5)


def test_product_negative_quantity_raises():
    with pytest.raises(ValidationError):
        Product("PRD-1", "SKU", "Товар", 10.0, -1)


def test_available_quantity_without_reserve():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 40)
    assert p.available_quantity == 40


def test_available_quantity_with_reserve():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 40)
    p.add_reservation(15)
    assert p.available_quantity == 25


def test_is_active_true_for_new_product():
    p = Product("PRD-1", "SKU", "Товар", 10.0)
    assert p.is_active is True


def test_needs_reorder_when_below_min():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 5, 10)
    assert p.needs_reorder is True


def test_needs_reorder_false_when_above_min():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 20, 10)
    assert p.needs_reorder is False


def test_increase_stock():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    p.increase_stock(5)
    assert p.quantity_on_hand == 15


def test_increase_stock_zero_raises():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    with pytest.raises(ValidationError):
        p.increase_stock(0)


def test_increase_stock_negative_raises():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    with pytest.raises(ValidationError):
        p.increase_stock(-3)


def test_decrease_stock():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    p.decrease_stock(4)
    assert p.quantity_on_hand == 6


def test_decrease_stock_too_much_raises():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    with pytest.raises(ValidationError):
        p.decrease_stock(11)


def test_decrease_stock_zero_raises():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    with pytest.raises(ValidationError):
        p.decrease_stock(0)


def test_add_reservation():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    p.add_reservation(3)
    assert p.reserved_quantity == 3


def test_add_reservation_more_than_available_raises():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    with pytest.raises(ValidationError):
        p.add_reservation(11)


def test_add_reservation_zero_raises():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    with pytest.raises(ValidationError):
        p.add_reservation(0)


def test_release_reservation():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    p.add_reservation(5)
    p.release_reservation(2)
    assert p.reserved_quantity == 3


def test_release_more_than_reserved_raises():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    p.add_reservation(2)
    with pytest.raises(ValidationError):
        p.release_reservation(3)


def test_release_reservation_zero_raises():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 10)
    with pytest.raises(ValidationError):
        p.release_reservation(0)


def test_discontinue_changes_status():
    p = Product("PRD-1", "SKU", "Товар", 10.0)
    p.discontinue()
    assert p.status == ProductStatus.DISCONTINUED
    assert p.is_active is False


def test_product_equality_by_id():
    a = Product("PRD-1", "SKU-A", "Товар А", 10.0)
    b = Product("PRD-1", "SKU-B", "Товар Б", 20.0)
    assert a == b


def test_product_inequality_with_other_type():
    p = Product("PRD-1", "SKU", "Товар", 10.0)
    assert p != "PRD-1"


def test_product_hash_allows_set_usage():
    a = Product("PRD-1", "SKU-A", "Товар", 10.0)
    b = Product("PRD-1", "SKU-B", "Товар", 10.0)
    assert len({a, b}) == 1


def test_product_repr_contains_sku():
    p = Product("PRD-1", "SKU-9", "Товар", 10.0, 7)
    assert "SKU-9" in repr(p)


def test_reserve_then_available_reflects_change():
    p = Product("PRD-1", "SKU", "Товар", 10.0, 20)
    p.add_reservation(8)
    assert p.available_quantity == 12
    assert p.quantity_on_hand == 20
