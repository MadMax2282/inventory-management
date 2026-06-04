import pytest

from src.application import Application
from src.models.product import Product
from src.models.supplier import Supplier
from src.models.user import User
from src.storage.repositories import ProductRepository
from src.utils.enums import CustomerTier, UserRole


@pytest.fixture
def product():
    return Product("PRD-1", "SKU-1", "Тестовий товар", 100.0, 50, 10, 20)


@pytest.fixture
def supplier():
    return Supplier("SPL-1", "Постачальник", 3, 4.5)


@pytest.fixture
def manager():
    return User("USR-1", "Менеджер", UserRole.MANAGER)


@pytest.fixture
def vip_client():
    return User("USR-2", "Клієнт", UserRole.CLIENT, CustomerTier.VIP)


@pytest.fixture
def product_repository():
    return ProductRepository()


@pytest.fixture
def app():
    return Application()
