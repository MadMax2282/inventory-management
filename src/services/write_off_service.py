from src.models.write_off import WriteOff
from src.utils.enums import WriteOffReason
from src.utils.exceptions import InsufficientStockError
from src.utils.id_generator import IdGenerator


class WriteOffService:
    """Сервіс списання браку. Зменшує залишок і фіксує фінансовий збиток."""

    # коефіцієнт залишкової вартості для різних причин списання
    RECOVERY_RATE = {
        WriteOffReason.DEFECT: 0.0,
        WriteOffReason.EXPIRED: 0.0,
        WriteOffReason.DAMAGED: 0.3,
        WriteOffReason.LOST: 0.0,
    }

    def __init__(self, write_off_repository, inventory_service):
        self._write_offs = write_off_repository
        self._inventory = inventory_service
        self._write_off_ids = IdGenerator("WRF")

    def write_off(self, product_id, quantity, reason=WriteOffReason.DEFECT):
        product = self._inventory.get_product(product_id)
        if quantity > product.available_quantity:
            raise InsufficientStockError(
                "Не можна списати більше доступного залишку товару {}".format(product.sku)
            )
        record = WriteOff(self._write_off_ids.next_id(), product_id, quantity, reason)
        record.set_loss(self._calculate_loss(product, quantity, reason))
        self._inventory.adjust_stock(product_id, -quantity)
        self._write_offs.add(record)
        return record

    def _calculate_loss(self, product, quantity, reason):
        full_value = product.unit_price * quantity
        recovery = self.RECOVERY_RATE.get(reason, 0.0)
        return full_value * (1 - recovery)

    def total_loss(self):
        return round(sum(w.loss_amount for w in self._write_offs.get_all()), 2)

    def history_for(self, product_id):
        return self._write_offs.get_for_product(product_id)
