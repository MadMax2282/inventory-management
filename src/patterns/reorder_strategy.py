import math
from abc import ABC, abstractmethod

from src.utils.validators import require_positive


class ReorderStrategy(ABC):
    """Інтерфейс стратегії розрахунку обсягу перезамовлення товару."""

    @abstractmethod
    def calculate(self, product):
        raise NotImplementedError


class FixedQuantityStrategy(ReorderStrategy):
    """Замовляємо фіксований обсяг, що заданий у самому товарі."""

    def calculate(self, product):
        if product.reorder_quantity > 0:
            return product.reorder_quantity
        # запасний варіант, якщо обсяг не налаштовано
        return max(product.min_stock_level, 1)


class MinMaxStrategy(ReorderStrategy):
    """Поповнюємо запас до верхньої межі, що кратна мінімальному рівню."""

    def __init__(self, max_factor=2):
        self.max_factor = max_factor

    def calculate(self, product):
        target = product.min_stock_level * self.max_factor
        deficit = target - product.available_quantity
        return deficit if deficit > 0 else 0


class EconomicOrderQuantityStrategy(ReorderStrategy):
    """Класична формула EOQ на основі попиту, вартості замовлення та зберігання."""

    def __init__(self, annual_demand, order_cost, holding_cost):
        self.annual_demand = require_positive(annual_demand, "annual_demand")
        self.order_cost = require_positive(order_cost, "order_cost")
        self.holding_cost = require_positive(holding_cost, "holding_cost")

    def calculate(self, product):
        value = (2 * self.annual_demand * self.order_cost) / self.holding_cost
        return int(math.ceil(math.sqrt(value)))
