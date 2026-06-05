import pytest

from src.models.product import Product
from src.patterns.reorder_strategy import (
    EconomicOrderQuantityStrategy,
    FixedQuantityStrategy,
    MinMaxStrategy,
)
from src.utils.exceptions import ValidationError


def make_product(qty=5, minimum=10, reorder=20):
    return Product("PRD-1", "SKU-1", "Товар", 10.0, qty, minimum, reorder)


def test_fixed_quantity_uses_reorder_field():
    strategy = FixedQuantityStrategy()
    assert strategy.calculate(make_product(reorder=20)) == 20


def test_fixed_quantity_fallback_to_min():
    strategy = FixedQuantityStrategy()
    product = make_product(minimum=8, reorder=0)
    assert strategy.calculate(product) == 8


def test_fixed_quantity_fallback_min_zero():
    strategy = FixedQuantityStrategy()
    product = make_product(minimum=0, reorder=0)
    assert strategy.calculate(product) == 1


def test_min_max_default_factor():
    strategy = MinMaxStrategy()
    product = make_product(qty=4, minimum=10)
    # ціль 10*2=20, дефіцит 20-4=16
    assert strategy.calculate(product) == 16


def test_min_max_custom_factor():
    strategy = MinMaxStrategy(max_factor=3)
    product = make_product(qty=5, minimum=10)
    assert strategy.calculate(product) == 25


def test_min_max_no_deficit_returns_zero():
    strategy = MinMaxStrategy(max_factor=2)
    product = make_product(qty=30, minimum=10)
    assert strategy.calculate(product) == 0


def test_eoq_basic_calculation():
    strategy = EconomicOrderQuantityStrategy(annual_demand=1000, order_cost=10,
                                             holding_cost=2)
    # sqrt(2*1000*10/2) = sqrt(10000) = 100
    assert strategy.calculate(make_product()) == 100


def test_eoq_rounds_up():
    strategy = EconomicOrderQuantityStrategy(annual_demand=1200, order_cost=8,
                                             holding_cost=3)
    value = strategy.calculate(make_product())
    assert value == 80


def test_eoq_invalid_demand_raises():
    with pytest.raises(ValidationError):
        EconomicOrderQuantityStrategy(annual_demand=0, order_cost=10, holding_cost=2)


def test_eoq_invalid_holding_raises():
    with pytest.raises(ValidationError):
        EconomicOrderQuantityStrategy(annual_demand=100, order_cost=10, holding_cost=0)


def test_min_max_accounts_for_reserved():
    strategy = MinMaxStrategy(max_factor=2)
    product = make_product(qty=20, minimum=10)
    product.add_reservation(15)
    # доступно 20-15=5, ціль 20, дефіцит 15
    assert strategy.calculate(product) == 15
