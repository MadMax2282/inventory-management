from src.patterns.reorder_strategy import FixedQuantityStrategy


class ReorderService:
    """Сервіс перезамовлення. За стратегією рахує обсяг та формує пропозиції закупівлі."""

    def __init__(self, inventory_service, strategy=None):
        self._inventory = inventory_service
        self._strategy = strategy or FixedQuantityStrategy()

    def set_strategy(self, strategy):
        self._strategy = strategy

    def products_to_reorder(self):
        return [
            p for p in self._inventory.list_products()
            if p.is_active and p.needs_reorder
        ]

    def suggest_for(self, product_id):
        product = self._inventory.get_product(product_id)
        if not product.needs_reorder:
            return 0
        return self._strategy.calculate(product)

    def build_reorder_plan(self):
        """Повертає список пропозицій у форматі товар та рекомендований обсяг."""
        plan = []
        for product in self.products_to_reorder():
            quantity = self._strategy.calculate(product)
            if quantity > 0:
                plan.append({"product_id": product.id, "sku": product.sku,
                             "quantity": quantity})
                self._inventory.subject.notify(
                    "reorder", product, {"quantity": quantity}
                )
        return plan
