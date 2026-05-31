from src.utils.enums import TIER_PRIORITY, CustomerTier, ReservationStatus
from src.utils.exceptions import InvalidStateError
from src.utils.validators import require_non_empty, require_positive


class Reservation:
    """Резервування товару клієнтом. Пріоритет залежить від рівня клієнта."""

    def __init__(self, reservation_id, product_id, customer_id, quantity,
                 tier=CustomerTier.REGULAR, sequence=0):
        self.id = require_non_empty(reservation_id, "id")
        self.product_id = require_non_empty(product_id, "product_id")
        self.customer_id = require_non_empty(customer_id, "customer_id")
        self.quantity = require_positive(quantity, "quantity")
        self.tier = tier
        # порядковий номер для розвʼязання конфлікту однакових пріоритетів за FIFO
        self.sequence = sequence
        self.status = ReservationStatus.PENDING

    @property
    def priority_value(self):
        return TIER_PRIORITY.get(self.tier, 1)

    def allocate(self):
        if self.status != ReservationStatus.PENDING:
            raise InvalidStateError("Виділити товар можна лише для очікуваного резерву")
        self.status = ReservationStatus.ALLOCATED

    def fulfill(self):
        if self.status != ReservationStatus.ALLOCATED:
            raise InvalidStateError("Видати можна лише виділений резерв")
        self.status = ReservationStatus.FULFILLED

    def cancel(self):
        if self.status == ReservationStatus.FULFILLED:
            raise InvalidStateError("Виконаний резерв скасувати не можна")
        self.status = ReservationStatus.CANCELLED

    def expire(self):
        if self.status in (ReservationStatus.FULFILLED, ReservationStatus.CANCELLED):
            raise InvalidStateError("Цей резерв вже завершено")
        self.status = ReservationStatus.EXPIRED

    @property
    def is_active(self):
        return self.status in (ReservationStatus.PENDING, ReservationStatus.ALLOCATED)

    def __repr__(self):
        return "Reservation(id={}, product={}, qty={})".format(
            self.id, self.product_id, self.quantity
        )
