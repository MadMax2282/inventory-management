from src.application import Application
from src.patterns.discount_strategy import TierDiscount
from src.patterns.reorder_strategy import MinMaxStrategy
from src.patterns.stock_observer import (
    LowStockNotifier,
    ReorderLogger,
    ReservationAvailabilityNotifier,
)
from src.utils.enums import CustomerTier, WriteOffReason


def run_demo():
    app = Application(discount_strategy=TierDiscount(),
                      reorder_strategy=MinMaxStrategy(max_factor=3))

    low_stock = LowStockNotifier()
    reorder_log = ReorderLogger()
    reservation_notifier = ReservationAvailabilityNotifier()
    app.inventory.subject.attach(low_stock)
    app.inventory.subject.attach(reorder_log)
    app.inventory.subject.attach(reservation_notifier)

    supplier = app.supply.register_supplier("ТОВ Дистрибуція", lead_time_days=3)
    laptop = app.inventory.register_product("SKU-100", "Ноутбук", 25000, 0, 5, 10)
    mouse = app.inventory.register_product("SKU-200", "Миша", 500, 0, 10, 20)

    supply = app.supply.create_supply(supplier.id)
    app.supply.add_item(supply.id, laptop.id, 8, 22000)
    app.supply.add_item(supply.id, mouse.id, 15, 350)
    app.supply.confirm_supply(supply.id)
    app.supply.receive_supply(supply.id)
    print("Залишок після поставки:", laptop.quantity_on_hand, mouse.quantity_on_hand)

    r_vip = app.reservation.create_reservation(laptop.id, "client-1", 3, CustomerTier.VIP)
    r_reg = app.reservation.create_reservation(laptop.id, "client-2", 4, CustomerTier.REGULAR)
    app.reservation.allocate_pending(laptop.id)
    print("Сповіщені клієнти:", reservation_notifier.notified_customers)

    sale = app.sales_service.create_sale("seller-1", "client-3")
    app.sales_service.add_item(sale.id, mouse.id, 5)
    app.sales_service.complete_sale(sale.id, CustomerTier.GOLD)
    print("Сума продажу зі знижкою:", sale.total)

    app.write_off.write_off(mouse.id, 2, WriteOffReason.DEFECT)
    print("Загальний збиток від списання:", app.write_off.total_loss())

    app.reservation.fulfill_reservation(r_vip.id)
    plan = app.reorder.build_reorder_plan()
    print("План перезамовлення:", plan)
    print("Повідомлення про низький залишок:", low_stock.messages)
    print("Журнал перезамовлень:", reorder_log.entries)


if __name__ == "__main__":
    run_demo()
