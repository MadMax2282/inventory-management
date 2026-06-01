from src.models.write_off import StockMovement
from src.utils.enums import MovementType


class MovementFactory:
    """Фабрика записів руху товару. Інкапсулює створення різних типів рухів."""

    def __init__(self, id_generator):
        self._id_generator = id_generator

    def _create(self, product_id, movement_type, quantity, note):
        return StockMovement(
            self._id_generator.next_id(), product_id, movement_type, quantity, note
        )

    def inbound(self, product_id, quantity, note="Прибуття за поставкою"):
        return self._create(product_id, MovementType.INBOUND, quantity, note)

    def outbound(self, product_id, quantity, note="Відвантаження за продажем"):
        return self._create(product_id, MovementType.OUTBOUND, -quantity, note)

    def reserve(self, product_id, quantity, note="Резервування"):
        return self._create(product_id, MovementType.RESERVE, quantity, note)

    def release(self, product_id, quantity, note="Зняття резерву"):
        return self._create(product_id, MovementType.RELEASE, quantity, note)

    def write_off(self, product_id, quantity, note="Списання браку"):
        return self._create(product_id, MovementType.WRITE_OFF, -quantity, note)

    def adjustment(self, product_id, quantity, note="Коригування залишку"):
        return self._create(product_id, MovementType.ADJUSTMENT, quantity, note)
