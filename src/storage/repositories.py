from src.storage.in_memory_repository import InMemoryRepository


class ProductRepository(InMemoryRepository):
    def get_by_sku(self, sku):
        matches = self.find(lambda p: p.sku == sku)
        return matches[0] if matches else None

    def get_active(self):
        return self.find(lambda p: p.is_active)

    def get_below_min(self):
        return self.find(lambda p: p.needs_reorder)


class SupplierRepository(InMemoryRepository):
    def get_active(self):
        return self.find(lambda s: s.active)


class SupplyRepository(InMemoryRepository):
    def get_by_supplier(self, supplier_id):
        return self.find(lambda s: s.supplier_id == supplier_id)


class SaleRepository(InMemoryRepository):
    def get_by_seller(self, seller_id):
        return self.find(lambda s: s.seller_id == seller_id)


class ReservationRepository(InMemoryRepository):
    def get_for_product(self, product_id):
        return self.find(lambda r: r.product_id == product_id)

    def get_active_for_product(self, product_id):
        return self.find(lambda r: r.product_id == product_id and r.is_active)


class WriteOffRepository(InMemoryRepository):
    def get_for_product(self, product_id):
        return self.find(lambda w: w.product_id == product_id)


class MovementRepository(InMemoryRepository):
    def get_for_product(self, product_id):
        return self.find(lambda m: m.product_id == product_id)


class UserRepository(InMemoryRepository):
    def get_managers(self):
        return self.find(lambda u: u.is_manager)
