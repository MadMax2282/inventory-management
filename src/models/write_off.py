from src.utils.enums import MovementType, WriteOffReason
from src.utils.validators import require_non_empty, require_positive


class WriteOff:
    """Списання товару зі складу через брак, псування або втрату."""

    def __init__(self, write_off_id, product_id, quantity, reason=WriteOffReason.DEFECT):
        self.id = require_non_empty(write_off_id, "id")
        self.product_id = require_non_empty(product_id, "product_id")
        self.quantity = require_positive(quantity, "quantity")
        self.reason = reason
        self.loss_amount = 0.0

    def set_loss(self, amount):
        self.loss_amount = round(amount, 2)

    def __repr__(self):
        return "WriteOff(id={}, product={}, qty={})".format(
            self.id, self.product_id, self.quantity
        )


class StockMovement:
    """Запис історії руху товару для аудиту операцій складу."""

    def __init__(self, movement_id, product_id, movement_type, quantity, note=""):
        self.id = require_non_empty(movement_id, "id")
        self.product_id = require_non_empty(product_id, "product_id")
        self.movement_type = movement_type
        self.quantity = quantity
        self.note = note

    @property
    def is_inbound(self):
        return self.movement_type == MovementType.INBOUND

    def __repr__(self):
        return "StockMovement(product={}, type={}, qty={})".format(
            self.product_id, self.movement_type.value, self.quantity
        )
