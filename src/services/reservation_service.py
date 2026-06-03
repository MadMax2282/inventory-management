from src.models.reservation import Reservation
from src.utils.enums import CustomerTier, ReservationStatus
from src.utils.exceptions import InvalidStateError, ReservationError
from src.utils.id_generator import IdGenerator


class ReservationService:
    """Сервіс резервування. Розподіляє вільний товар між заявками за пріоритетом."""

    def __init__(self, reservation_repository, inventory_service):
        self._reservations = reservation_repository
        self._inventory = inventory_service
        self._reservation_ids = IdGenerator("RES")
        # лічильник для збереження порядку надходження заявок
        self._sequence = 0

    def create_reservation(self, product_id, customer_id, quantity,
                           tier=CustomerTier.REGULAR):
        product = self._inventory.get_product(product_id)
        if not product.is_active:
            raise ReservationError("Товар {} недоступний для резерву".format(product.sku))
        self._sequence += 1
        reservation = Reservation(
            self._reservation_ids.next_id(),
            product_id,
            customer_id,
            quantity,
            tier,
            self._sequence,
        )
        self._reservations.add(reservation)
        return reservation

    def allocate_pending(self, product_id):
        """Виділяє вільний товар очікуваним заявкам за спаданням пріоритету.

        Якщо для заявки не вистачає вільного товару, вона пропускається,
        а алгоритм переходить до наступної. Так дорогий запас не блокується
        однією великою заявкою.
        """
        product = self._inventory.get_product(product_id)
        pending = [
            r for r in self._reservations.get_for_product(product_id)
            if r.status == ReservationStatus.PENDING
        ]
        ordered = sorted(pending, key=lambda r: (-r.priority_value, r.sequence))
        allocated = []
        for reservation in ordered:
            if reservation.quantity <= product.available_quantity:
                self._inventory.reserve_stock(product_id, reservation.quantity)
                reservation.allocate()
                self._reservations.update(reservation)
                allocated.append(reservation)
                self._inventory.subject.notify(
                    "reservation_allocated",
                    product,
                    {"customer_id": reservation.customer_id,
                     "reservation_id": reservation.id},
                )
        return allocated

    def fulfill_reservation(self, reservation_id):
        reservation = self._reservations.get(reservation_id)
        if reservation.status != ReservationStatus.ALLOCATED:
            raise InvalidStateError("Видати можна лише виділений резерв")
        self._inventory.fulfill_reserved(reservation.product_id, reservation.quantity)
        reservation.fulfill()
        self._reservations.update(reservation)
        return reservation

    def cancel_reservation(self, reservation_id):
        reservation = self._reservations.get(reservation_id)
        if reservation.status == ReservationStatus.ALLOCATED:
            self._inventory.release_stock(reservation.product_id, reservation.quantity)
        reservation.cancel()
        self._reservations.update(reservation)
        return reservation

    def expire_reservation(self, reservation_id):
        reservation = self._reservations.get(reservation_id)
        if reservation.status == ReservationStatus.ALLOCATED:
            self._inventory.release_stock(reservation.product_id, reservation.quantity)
        reservation.expire()
        self._reservations.update(reservation)
        return reservation

    def active_for_product(self, product_id):
        return self._reservations.get_active_for_product(product_id)

    def get_reservation(self, reservation_id):
        return self._reservations.get(reservation_id)
