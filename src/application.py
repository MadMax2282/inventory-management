from src.services.inventory_service import InventoryService
from src.services.reorder_service import ReorderService
from src.services.reservation_service import ReservationService
from src.services.sales_service import SalesService
from src.services.supply_service import SupplyService
from src.services.write_off_service import WriteOffService
from src.storage.repositories import (
    MovementRepository,
    ProductRepository,
    ReservationRepository,
    SaleRepository,
    SupplierRepository,
    SupplyRepository,
    UserRepository,
    WriteOffRepository,
)


class Application:
    """Збирає сервіси на спільних сховищах. Точка входу для сценаріїв роботи."""

    def __init__(self, discount_strategy=None, reorder_strategy=None):
        self.products = ProductRepository()
        self.suppliers = SupplierRepository()
        self.supplies = SupplyRepository()
        self.sales = SaleRepository()
        self.reservations = ReservationRepository()
        self.write_offs = WriteOffRepository()
        self.movements = MovementRepository()
        self.users = UserRepository()

        self.inventory = InventoryService(self.products, self.movements)
        self.supply = SupplyService(self.supplies, self.suppliers, self.inventory)
        self.sales_service = SalesService(self.sales, self.inventory, discount_strategy)
        self.reservation = ReservationService(self.reservations, self.inventory)
        self.reorder = ReorderService(self.inventory, reorder_strategy)
        self.write_off = WriteOffService(self.write_offs, self.inventory)
