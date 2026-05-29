from enum import Enum


class ProductStatus(str, Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"


class SupplyStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class SaleStatus(str, Enum):
    NEW = "new"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    ALLOCATED = "allocated"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class CustomerTier(str, Enum):
    REGULAR = "regular"
    SILVER = "silver"
    GOLD = "gold"
    VIP = "vip"


class WriteOffReason(str, Enum):
    DEFECT = "defect"
    EXPIRED = "expired"
    DAMAGED = "damaged"
    LOST = "lost"


class MovementType(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    RESERVE = "reserve"
    RELEASE = "release"
    WRITE_OFF = "write_off"
    ADJUSTMENT = "adjustment"


class UserRole(str, Enum):
    MANAGER = "manager"
    SELLER = "seller"
    CLIENT = "client"


# числове значення пріоритету для рівнів клієнтів, більше значення обслуговується першим
TIER_PRIORITY = {
    CustomerTier.REGULAR: 1,
    CustomerTier.SILVER: 2,
    CustomerTier.GOLD: 3,
    CustomerTier.VIP: 4,
}
