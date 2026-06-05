import pytest

from src.models.product import Product
from src.storage.in_memory_repository import InMemoryRepository
from src.storage.repositories import (
    ProductRepository,
    ReservationRepository,
    SupplierRepository,
    UserRepository,
)
from src.models.reservation import Reservation
from src.models.supplier import Supplier
from src.models.user import User
from src.utils.enums import UserRole
from src.utils.exceptions import DuplicateEntityError, EntityNotFoundError


def make_product(pid="PRD-1", sku="SKU-1", qty=10, minimum=0):
    return Product(pid, sku, "Товар", 10.0, qty, minimum)


def test_add_and_get():
    repo = InMemoryRepository()
    p = make_product()
    repo.add(p)
    assert repo.get("PRD-1") is p


def test_add_duplicate_raises():
    repo = InMemoryRepository()
    repo.add(make_product())
    with pytest.raises(DuplicateEntityError):
        repo.add(make_product())


def test_get_missing_raises():
    repo = InMemoryRepository()
    with pytest.raises(EntityNotFoundError):
        repo.get("missing")


def test_get_all_returns_list():
    repo = InMemoryRepository()
    repo.add(make_product("PRD-1", "SKU-1"))
    repo.add(make_product("PRD-2", "SKU-2"))
    assert len(repo.get_all()) == 2


def test_update_existing():
    repo = InMemoryRepository()
    p = make_product()
    repo.add(p)
    p.name = "Оновлено"
    repo.update(p)
    assert repo.get("PRD-1").name == "Оновлено"


def test_update_missing_raises():
    repo = InMemoryRepository()
    with pytest.raises(EntityNotFoundError):
        repo.update(make_product())


def test_delete_existing():
    repo = InMemoryRepository()
    repo.add(make_product())
    repo.delete("PRD-1")
    assert repo.exists("PRD-1") is False


def test_delete_missing_raises():
    repo = InMemoryRepository()
    with pytest.raises(EntityNotFoundError):
        repo.delete("missing")


def test_exists_true_false():
    repo = InMemoryRepository()
    repo.add(make_product())
    assert repo.exists("PRD-1") is True
    assert repo.exists("PRD-2") is False


def test_find_predicate():
    repo = InMemoryRepository()
    repo.add(make_product("PRD-1", "SKU-1", qty=5))
    repo.add(make_product("PRD-2", "SKU-2", qty=50))
    found = repo.find(lambda p: p.quantity_on_hand > 10)
    assert len(found) == 1


def test_count():
    repo = InMemoryRepository()
    repo.add(make_product("PRD-1", "SKU-1"))
    assert repo.count() == 1


def test_clear():
    repo = InMemoryRepository()
    repo.add(make_product())
    repo.clear()
    assert repo.count() == 0


def test_product_repo_get_by_sku():
    repo = ProductRepository()
    repo.add(make_product("PRD-1", "SKU-A"))
    assert repo.get_by_sku("SKU-A").id == "PRD-1"


def test_product_repo_get_by_sku_missing():
    repo = ProductRepository()
    assert repo.get_by_sku("UNKNOWN") is None


def test_product_repo_get_active():
    repo = ProductRepository()
    p1 = make_product("PRD-1", "SKU-1")
    p2 = make_product("PRD-2", "SKU-2")
    p2.discontinue()
    repo.add(p1)
    repo.add(p2)
    assert len(repo.get_active()) == 1


def test_product_repo_get_below_min():
    repo = ProductRepository()
    repo.add(make_product("PRD-1", "SKU-1", qty=2, minimum=10))
    repo.add(make_product("PRD-2", "SKU-2", qty=50, minimum=10))
    assert len(repo.get_below_min()) == 1


def test_supplier_repo_get_active():
    repo = SupplierRepository()
    a = Supplier("SPL-1", "A")
    b = Supplier("SPL-2", "B")
    b.deactivate()
    repo.add(a)
    repo.add(b)
    assert len(repo.get_active()) == 1


def test_reservation_repo_for_product():
    repo = ReservationRepository()
    repo.add(Reservation("RES-1", "PRD-1", "c1", 2))
    repo.add(Reservation("RES-2", "PRD-2", "c2", 2))
    assert len(repo.get_for_product("PRD-1")) == 1


def test_reservation_repo_active_for_product():
    repo = ReservationRepository()
    active = Reservation("RES-1", "PRD-1", "c1", 2)
    done = Reservation("RES-2", "PRD-1", "c2", 2)
    done.cancel()
    repo.add(active)
    repo.add(done)
    assert len(repo.get_active_for_product("PRD-1")) == 1


def test_user_repo_get_managers():
    repo = UserRepository()
    repo.add(User("USR-1", "M", UserRole.MANAGER))
    repo.add(User("USR-2", "C", UserRole.CLIENT))
    assert len(repo.get_managers()) == 1
