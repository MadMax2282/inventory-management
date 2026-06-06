from abc import ABC, abstractmethod


class StockObserver(ABC):
    """Спостерігач за подіями складу."""

    @abstractmethod
    def on_event(self, event_type, product, payload):
        raise NotImplementedError


class StockSubject:
    """Субʼєкт спостереження. Розсилає події всім підписаним спостерігачам."""

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type, product, payload=None):
        for observer in self._observers[:]:
            observer.on_event(event_type, product, payload or {})

    @property
    def observer_count(self):
        return len(self._observers)


class LowStockNotifier(StockObserver):
    """Збирає сповіщення про товари, що опустились нижче мінімального рівня."""

    def __init__(self):
        self.messages = []

    def on_event(self, event_type, product, payload):
        if event_type == "low_stock":
            self.messages.append(
                "Низький залишок товару {}: доступно {}".format(
                    product.sku, product.available_quantity
                )
            )


class ReorderLogger(StockObserver):
    """Веде журнал запущених перезамовлень."""

    def __init__(self):
        self.entries = []

    def on_event(self, event_type, product, payload):
        if event_type == "reorder":
            self.entries.append(
                {"product_id": product.id, "quantity": payload.get("quantity", 0)}
            )


class ReservationAvailabilityNotifier(StockObserver):
    """Повідомляє клієнтів, коли зарезервований товар став доступним."""

    def __init__(self):
        self.notified_customers = []

    def on_event(self, event_type, product, payload):
        if event_type == "reservation_allocated":
            self.notified_customers.append(payload.get("customer_id"))
