"""Слой доступа к данным для учебного проекта HomeBudget (SQLite)."""
from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "database" / "homebudget.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
SEED_PATH = PROJECT_ROOT / "database" / "seed.sql"


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Открывает соединение и включает контроль внешних ключей SQLite."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path: str | Path = DEFAULT_DB_PATH, seed: bool = True) -> None:
    """Создаёт таблицы; тестовые строки добавляются идемпотентно."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with connect(db_path) as connection:
        connection.executescript(schema)
        if seed:
            seed_sql = SEED_PATH.read_text(encoding="utf-8")
            connection.executescript(seed_sql)


def list_products(db_path: str | Path = DEFAULT_DB_PATH) -> list[sqlite3.Row]:
    with connect(db_path) as connection:
        return connection.execute(
            """SELECT p.product_id, p.name, c.name AS category, p.unit,
                      p.quantity_on_hand, p.min_quantity, p.is_active
               FROM products AS p
               JOIN categories AS c ON c.category_id = p.category_id
               ORDER BY c.name, p.name"""
        ).fetchall()


def list_purchases(db_path: str | Path = DEFAULT_DB_PATH) -> list[sqlite3.Row]:
    with connect(db_path) as connection:
        return connection.execute(
            """SELECT pu.purchase_id, pu.purchase_date, pu.store, u.full_name,
                      COUNT(pi.item_id) AS item_count,
                      COALESCE(SUM(pi.quantity * pi.unit_price), 0) AS calculated_total,
                      e.amount AS recorded_total
               FROM purchases AS pu
               JOIN users AS u ON u.user_id = pu.user_id
               LEFT JOIN purchase_items AS pi ON pi.purchase_id = pu.purchase_id
               LEFT JOIN expenses AS e ON e.purchase_id = pu.purchase_id
               GROUP BY pu.purchase_id, pu.purchase_date, pu.store, u.full_name, e.amount
               ORDER BY pu.purchase_date DESC, pu.purchase_id DESC"""
        ).fetchall()


def list_expenses(db_path: str | Path = DEFAULT_DB_PATH) -> list[sqlite3.Row]:
    with connect(db_path) as connection:
        return connection.execute(
            """SELECT e.expense_id, e.expense_date, e.amount, e.description,
                      pu.store, pu.purchase_id
               FROM expenses AS e
               JOIN purchases AS pu ON pu.purchase_id = e.purchase_id
               ORDER BY e.expense_date DESC, e.expense_id DESC"""
        ).fetchall()


def dashboard(db_path: str | Path = DEFAULT_DB_PATH) -> dict[str, float | int]:
    with connect(db_path) as connection:
        products_count = connection.execute(
            "SELECT COUNT(*) FROM products WHERE is_active = 1"
        ).fetchone()[0]
        purchases_count = connection.execute(
            "SELECT COUNT(*) FROM purchases"
        ).fetchone()[0]
        spent = connection.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        ).fetchone()[0]
        low_stock = connection.execute(
            """SELECT COUNT(*) FROM products
               WHERE is_active = 1 AND quantity_on_hand <= min_quantity"""
        ).fetchone()[0]
    return {
        "products_count": int(products_count),
        "purchases_count": int(purchases_count),
        "spent": float(spent),
        "low_stock": int(low_stock),
    }


def add_product(
    name: str,
    category_name: str,
    unit: str,
    quantity_on_hand: float = 0,
    min_quantity: float = 0,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    """Добавляет товар; категорию создаёт при необходимости."""
    name = name.strip()
    category_name = category_name.strip()
    unit = unit.strip()
    if not name or not category_name or not unit:
        raise ValueError("Название товара, категория и единица измерения обязательны.")
    if quantity_on_hand < 0 or min_quantity < 0:
        raise ValueError("Количество и минимальный остаток не могут быть отрицательными.")
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT category_id FROM categories WHERE name = ?", (category_name,)
        ).fetchone()
        if row is None:
            cursor = connection.execute(
                "INSERT INTO categories(name, description) VALUES (?, ?)",
                (category_name, "Категория добавлена пользователем"),
            )
            category_id = int(cursor.lastrowid)
        else:
            category_id = int(row["category_id"])
        cursor = connection.execute(
            """INSERT INTO products
               (name, category_id, unit, quantity_on_hand, min_quantity, is_active)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (name, category_id, unit, quantity_on_hand, min_quantity),
        )
        return int(cursor.lastrowid)


def create_purchase(
    user_id: int,
    store: str,
    items: Sequence[tuple[int, float, float]],
    purchase_date: str | None = None,
    note: str = "",
    db_path: str | Path = DEFAULT_DB_PATH,
) -> tuple[int, float]:
    """Регистрирует покупку, её позиции и соответствующий расход в одной транзакции.

    items: последовательность кортежей (product_id, quantity, unit_price).
    При успешной регистрации остаток товара увеличивается на купленное количество.
    """
    if not items:
        raise ValueError("Покупка должна содержать хотя бы один товар.")
    normalized: dict[int, tuple[float, float]] = {}
    for product_id, quantity, unit_price in items:
        if product_id <= 0 or quantity <= 0 or unit_price < 0:
            raise ValueError("ID товара должен быть положительным, количество — больше 0, цена — неотрицательной.")
        if product_id in normalized:
            old_quantity, old_price = normalized[product_id]
            if old_price != float(unit_price):
                raise ValueError("Для одного товара в покупке указаны разные цены.")
            normalized[product_id] = (old_quantity + float(quantity), float(unit_price))
        else:
            normalized[product_id] = (float(quantity), float(unit_price))

    used_date = purchase_date or date.today().isoformat()
    used_store = store.strip() or "Не указан"
    total = round(sum(quantity * price for quantity, price in normalized.values()), 2)

    with connect(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO purchases(user_id, purchase_date, store, note) VALUES (?, ?, ?, ?)",
            (user_id, used_date, used_store, note.strip()),
        )
        purchase_id = int(cursor.lastrowid)
        for product_id, (quantity, unit_price) in normalized.items():
            product = connection.execute(
                "SELECT product_id, is_active FROM products WHERE product_id = ?",
                (product_id,),
            ).fetchone()
            if product is None:
                raise ValueError(f"Товар с ID {product_id} не найден.")
            if not product["is_active"]:
                raise ValueError(f"Товар с ID {product_id} неактивен.")
            connection.execute(
                """INSERT INTO purchase_items(purchase_id, product_id, quantity, unit_price)
                   VALUES (?, ?, ?, ?)""",
                (purchase_id, product_id, quantity, unit_price),
            )
            connection.execute(
                "UPDATE products SET quantity_on_hand = quantity_on_hand + ? WHERE product_id = ?",
                (quantity, product_id),
            )
        connection.execute(
            """INSERT INTO expenses(purchase_id, amount, expense_date, description)
               VALUES (?, ?, ?, ?)""",
            (purchase_id, total, used_date, f"Покупка в магазине «{used_store}»"),
        )
    return purchase_id, total
