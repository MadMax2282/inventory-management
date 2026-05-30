from src.utils.enums import CustomerTier, UserRole
from src.utils.validators import require_non_empty


class User:
    """Користувач системи. Для клієнтів зберігається рівень лояльності."""

    def __init__(self, user_id, name, role=UserRole.CLIENT, tier=CustomerTier.REGULAR):
        self.id = require_non_empty(user_id, "id")
        self.name = require_non_empty(name, "name")
        self.role = role
        self.tier = tier

    @property
    def is_manager(self):
        return self.role == UserRole.MANAGER

    def __repr__(self):
        return "User(id={}, role={})".format(self.id, self.role.value)

    def __eq__(self, other):
        return isinstance(other, User) and other.id == self.id

    def __hash__(self):
        return hash(self.id)
