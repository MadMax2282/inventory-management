from abc import ABC, abstractmethod

from src.utils.enums import CustomerTier


class DiscountStrategy(ABC):
    """Інтерфейс стратегії розрахунку знижки для продажу."""

    @abstractmethod
    def calculate(self, subtotal, customer_tier):
        raise NotImplementedError


class NoDiscount(DiscountStrategy):
    def calculate(self, subtotal, customer_tier):
        return 0.0


class TierDiscount(DiscountStrategy):
    """Знижка у відсотках, що залежить від рівня лояльності клієнта."""

    RATES = {
        CustomerTier.REGULAR: 0.0,
        CustomerTier.SILVER: 0.03,
        CustomerTier.GOLD: 0.07,
        CustomerTier.VIP: 0.12,
    }

    def calculate(self, subtotal, customer_tier):
        rate = self.RATES.get(customer_tier, 0.0)
        return round(subtotal * rate, 2)


class BulkDiscount(DiscountStrategy):
    """Знижка за великий чек: фіксований відсоток понад порогову суму."""

    def __init__(self, threshold=1000.0, rate=0.1):
        self.threshold = threshold
        self.rate = rate

    def calculate(self, subtotal, customer_tier):
        if subtotal >= self.threshold:
            return round(subtotal * self.rate, 2)
        return 0.0
