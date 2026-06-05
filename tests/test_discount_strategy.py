from src.patterns.discount_strategy import (
    BulkDiscount,
    NoDiscount,
    TierDiscount,
)
from src.utils.enums import CustomerTier


def test_no_discount_returns_zero():
    assert NoDiscount().calculate(500, CustomerTier.VIP) == 0.0


def test_tier_discount_regular_zero():
    assert TierDiscount().calculate(1000, CustomerTier.REGULAR) == 0.0


def test_tier_discount_silver():
    assert TierDiscount().calculate(1000, CustomerTier.SILVER) == 30.0


def test_tier_discount_gold():
    assert TierDiscount().calculate(1000, CustomerTier.GOLD) == 70.0


def test_tier_discount_vip():
    assert TierDiscount().calculate(1000, CustomerTier.VIP) == 120.0


def test_tier_discount_rounds():
    assert TierDiscount().calculate(333, CustomerTier.SILVER) == 9.99


def test_bulk_discount_below_threshold():
    strategy = BulkDiscount(threshold=1000, rate=0.1)
    assert strategy.calculate(500, CustomerTier.REGULAR) == 0.0


def test_bulk_discount_at_threshold():
    strategy = BulkDiscount(threshold=1000, rate=0.1)
    assert strategy.calculate(1000, CustomerTier.REGULAR) == 100.0


def test_bulk_discount_above_threshold():
    strategy = BulkDiscount(threshold=1000, rate=0.2)
    assert strategy.calculate(2000, CustomerTier.REGULAR) == 400.0


def test_bulk_discount_default_params():
    strategy = BulkDiscount()
    assert strategy.calculate(1500, CustomerTier.REGULAR) == 150.0
