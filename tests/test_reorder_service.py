import pytest

from src.services.inventory_service import InventoryService
from src.services.reorder_service import ReorderService
from src.patterns.reorder_strategy import (
    FixedQuantityStrategy,
    MinMaxStrategy,
)
from src.patterns.stock_observer import ReorderLogger
from src.storage.repositories import MovementRepository, ProductRepository


@pytest.fixture
def inventory():
    return InventoryService(ProductRepository(), MovementRepository())


@pytest.fixture
def service(inventory):
    return ReorderService(inventory)


def test_default_strategy_is_fixed(service):
    assert isinstance(service._strategy, FixedQuantityStrategy)


def test_set_strategy(service):
    strat = MinMaxStrategy(3)
    service.set_strategy(strat)
    assert service._strategy is strat


def test_no_products_to_reorder_when_stock_full(inventory, service):
    inventory.register_product("SKU-1", "Товар", 10.0, 100, 10, 20)
    assert service.products_to_reorder() == []


def test_product_below_min_is_listed(inventory, service):
    inventory.register_product("SKU-1", "Товар", 10.0, 5, 10, 20)
    items = service.products_to_reorder()
    assert len(items) == 1


def test_discontinued_product_skipped(inventory, service):
    p = inventory.register_product("SKU-1", "Товар", 10.0, 2, 10, 20)
    inventory.discontinue_product(p.id)
    assert service.products_to_reorder() == []


def test_suggest_for_returns_reorder_quantity(inventory, service):
    p = inventory.register_product("SKU-1", "Товар", 10.0, 5, 10, 25)
    assert service.suggest_for(p.id) == 25


def test_suggest_for_returns_zero_when_no_need(inventory, service):
    p = inventory.register_product("SKU-1", "Товар", 10.0, 100, 10, 25)
    assert service.suggest_for(p.id) == 0


def test_build_plan_contains_expected_fields(inventory, service):
    inventory.register_product("SKU-1", "Товар", 10.0, 5, 10, 25)
    plan = service.build_reorder_plan()
    assert plan[0]["sku"] == "SKU-1"
    assert plan[0]["quantity"] == 25


def test_build_plan_empty_when_nothing_needed(inventory, service):
    inventory.register_product("SKU-1", "Товар", 10.0, 100, 10, 25)
    assert service.build_reorder_plan() == []


def test_build_plan_with_min_max_strategy(inventory):
    inventory.register_product("SKU-1", "Товар", 10.0, 4, 10, 0)
    service = ReorderService(inventory, MinMaxStrategy(2))
    plan = service.build_reorder_plan()
    # ціль 20, доступно 4, отже бракує 16
    assert plan[0]["quantity"] == 16


def test_build_plan_notifies_observer(inventory):
    logger = ReorderLogger()
    inventory.subject.attach(logger)
    inventory.register_product("SKU-1", "Товар", 10.0, 5, 10, 25)
    service = ReorderService(inventory)
    service.build_reorder_plan()
    assert len(logger.entries) == 1


def test_plan_skips_zero_quantity(inventory):
    # якщо стратегія повертає 0, товар не додається до плану
    class ZeroStrategy:
        def calculate(self, product):
            return 0

    inventory.register_product("SKU-1", "Товар", 10.0, 5, 10, 25)
    service = ReorderService(inventory, ZeroStrategy())
    plan = service.build_reorder_plan()
    assert plan == []


def test_multiple_products_in_plan(inventory, service):
    inventory.register_product("SKU-1", "Товар A", 10.0, 2, 10, 20)
    inventory.register_product("SKU-2", "Товар B", 10.0, 1, 5, 15)
    inventory.register_product("SKU-3", "Товар C", 10.0, 50, 10, 20)
    plan = service.build_reorder_plan()
    assert len(plan) == 2
