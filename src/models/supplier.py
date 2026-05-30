from src.utils.exceptions import ValidationError
from src.utils.validators import require_non_empty, require_non_negative


class Supplier:
    """Постачальник товарів. Час доставки впливає на розрахунок перезамовлення."""

    def __init__(self, supplier_id, name, lead_time_days=1, rating=5.0):
        self.id = require_non_empty(supplier_id, "id")
        self.name = require_non_empty(name, "name")
        self.lead_time_days = require_non_negative(lead_time_days, "lead_time_days")
        self.rating = rating
        self.active = True

    def deactivate(self):
        self.active = False

    def update_rating(self, value):
        if value < 0 or value > 5:
            raise ValidationError("Рейтинг має бути в межах від 0 до 5")
        self.rating = value

    def __repr__(self):
        return "Supplier(id={}, name={})".format(self.id, self.name)

    def __eq__(self, other):
        return isinstance(other, Supplier) and other.id == self.id

    def __hash__(self):
        return hash(self.id)
