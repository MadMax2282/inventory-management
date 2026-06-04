import pytest

from src.models.supplier import Supplier
from src.models.user import User
from src.utils.enums import CustomerTier, UserRole
from src.utils.exceptions import ValidationError


def test_supplier_creation():
    s = Supplier("SPL-1", "Постачальник", 5, 4.0)
    assert s.id == "SPL-1"
    assert s.lead_time_days == 5
    assert s.rating == 4.0
    assert s.active is True


def test_supplier_default_lead_time():
    s = Supplier("SPL-1", "Постачальник")
    assert s.lead_time_days == 1


def test_supplier_empty_name_raises():
    with pytest.raises(ValidationError):
        Supplier("SPL-1", "")


def test_supplier_negative_lead_time_raises():
    with pytest.raises(ValidationError):
        Supplier("SPL-1", "Постачальник", -2)


def test_supplier_deactivate():
    s = Supplier("SPL-1", "Постачальник")
    s.deactivate()
    assert s.active is False


def test_supplier_update_rating():
    s = Supplier("SPL-1", "Постачальник")
    s.update_rating(3.5)
    assert s.rating == 3.5


def test_supplier_rating_too_high_raises():
    s = Supplier("SPL-1", "Постачальник")
    with pytest.raises(ValidationError):
        s.update_rating(6)


def test_supplier_rating_negative_raises():
    s = Supplier("SPL-1", "Постачальник")
    with pytest.raises(ValidationError):
        s.update_rating(-1)


def test_supplier_equality():
    a = Supplier("SPL-1", "А")
    b = Supplier("SPL-1", "Б")
    assert a == b


def test_supplier_hash():
    a = Supplier("SPL-1", "А")
    b = Supplier("SPL-1", "Б")
    assert len({a, b}) == 1


def test_supplier_repr():
    s = Supplier("SPL-1", "Назва")
    assert "Назва" in repr(s)


def test_user_creation_default_role():
    u = User("USR-1", "Іван")
    assert u.role == UserRole.CLIENT
    assert u.tier == CustomerTier.REGULAR


def test_user_manager_flag():
    u = User("USR-1", "Менеджер", UserRole.MANAGER)
    assert u.is_manager is True


def test_user_client_not_manager():
    u = User("USR-1", "Клієнт", UserRole.CLIENT)
    assert u.is_manager is False


def test_user_empty_name_raises():
    with pytest.raises(ValidationError):
        User("USR-1", "")


def test_user_equality():
    a = User("USR-1", "А")
    b = User("USR-1", "Б")
    assert a == b


def test_user_repr_contains_role():
    u = User("USR-1", "Іван", UserRole.SELLER)
    assert "seller" in repr(u)


def test_user_vip_tier():
    u = User("USR-1", "Клієнт", UserRole.CLIENT, CustomerTier.VIP)
    assert u.tier == CustomerTier.VIP
