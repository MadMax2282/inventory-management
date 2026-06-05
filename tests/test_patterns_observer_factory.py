from src.models.product import Product
from src.patterns.movement_factory import MovementFactory
from src.patterns.stock_observer import (
    LowStockNotifier,
    ReorderLogger,
    ReservationAvailabilityNotifier,
    StockSubject,
)
from src.utils.enums import MovementType
from src.utils.id_generator import IdGenerator


def make_product():
    return Product("PRD-1", "SKU-1", "Товар", 10.0, 3, 10)


def test_subject_attach_increases_count():
    subject = StockSubject()
    subject.attach(LowStockNotifier())
    assert subject.observer_count == 1


def test_subject_attach_same_twice_counts_once():
    subject = StockSubject()
    obs = LowStockNotifier()
    subject.attach(obs)
    subject.attach(obs)
    assert subject.observer_count == 1


def test_subject_detach():
    subject = StockSubject()
    obs = LowStockNotifier()
    subject.attach(obs)
    subject.detach(obs)
    assert subject.observer_count == 0


def test_subject_detach_missing_safe():
    subject = StockSubject()
    subject.detach(LowStockNotifier())
    assert subject.observer_count == 0


def test_low_stock_notifier_collects_message():
    subject = StockSubject()
    notifier = LowStockNotifier()
    subject.attach(notifier)
    subject.notify("low_stock", make_product())
    assert len(notifier.messages) == 1


def test_low_stock_notifier_ignores_other_events():
    notifier = LowStockNotifier()
    notifier.on_event("reorder", make_product(), {})
    assert notifier.messages == []


def test_reorder_logger_records_entry():
    logger = ReorderLogger()
    logger.on_event("reorder", make_product(), {"quantity": 12})
    assert logger.entries[0]["quantity"] == 12


def test_reorder_logger_ignores_other():
    logger = ReorderLogger()
    logger.on_event("low_stock", make_product(), {})
    assert logger.entries == []


def test_reservation_notifier_records_customer():
    notifier = ReservationAvailabilityNotifier()
    notifier.on_event("reservation_allocated", make_product(),
                      {"customer_id": "client-9"})
    assert notifier.notified_customers == ["client-9"]


def test_notify_reaches_multiple_observers():
    subject = StockSubject()
    low = LowStockNotifier()
    logger = ReorderLogger()
    subject.attach(low)
    subject.attach(logger)
    subject.notify("low_stock", make_product())
    assert len(low.messages) == 1
    assert logger.entries == []


def test_factory_inbound_positive_quantity():
    factory = MovementFactory(IdGenerator("MOV"))
    movement = factory.inbound("PRD-1", 5)
    assert movement.movement_type == MovementType.INBOUND
    assert movement.quantity == 5


def test_factory_outbound_negative_quantity():
    factory = MovementFactory(IdGenerator("MOV"))
    movement = factory.outbound("PRD-1", 5)
    assert movement.movement_type == MovementType.OUTBOUND
    assert movement.quantity == -5


def test_factory_reserve():
    factory = MovementFactory(IdGenerator("MOV"))
    movement = factory.reserve("PRD-1", 4)
    assert movement.movement_type == MovementType.RESERVE


def test_factory_release():
    factory = MovementFactory(IdGenerator("MOV"))
    movement = factory.release("PRD-1", 4)
    assert movement.movement_type == MovementType.RELEASE


def test_factory_write_off_negative():
    factory = MovementFactory(IdGenerator("MOV"))
    movement = factory.write_off("PRD-1", 2)
    assert movement.quantity == -2


def test_factory_adjustment():
    factory = MovementFactory(IdGenerator("MOV"))
    movement = factory.adjustment("PRD-1", -3)
    assert movement.movement_type == MovementType.ADJUSTMENT


def test_factory_generates_unique_ids():
    factory = MovementFactory(IdGenerator("MOV"))
    a = factory.inbound("PRD-1", 1)
    b = factory.inbound("PRD-1", 1)
    assert a.id != b.id
