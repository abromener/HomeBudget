"""Автоматические проверки слоя данных HomeBudget (стандартный unittest)."""
import tempfile
import unittest
from pathlib import Path

from src.database import (
    create_purchase,
    dashboard,
    initialize_database,
    list_expenses,
    list_products,
)


class HomeBudgetDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_homebudget.db"
        initialize_database(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_seed_data_is_loaded(self):
        self.assertGreaterEqual(len(list_products(self.db_path)), 5)
        self.assertEqual(dashboard(self.db_path)["purchases_count"], 2)

    def test_purchase_creates_expense_and_updates_stock(self):
        before = {row["product_id"]: row["quantity_on_hand"] for row in list_products(self.db_path)}
        purchase_id, total = create_purchase(1, "Тестовый магазин", [(1, 2, 50.0)], db_path=self.db_path)
        self.assertGreater(purchase_id, 0)
        self.assertEqual(total, 100.0)
        after = {row["product_id"]: row["quantity_on_hand"] for row in list_products(self.db_path)}
        self.assertEqual(after[1], before[1] + 2)
        self.assertTrue(any(row["amount"] == 100.0 for row in list_expenses(self.db_path)))

    def test_invalid_product_rolls_back_purchase(self):
        with self.assertRaises(ValueError):
            create_purchase(1, "Тестовый магазин", [(9999, 1, 10.0)], db_path=self.db_path)
        self.assertEqual(dashboard(self.db_path)["purchases_count"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
