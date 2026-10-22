"""Консольное приложение HomeBudget для демонстрации работы с SQLite."""
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .database import (
        DEFAULT_DB_PATH,
        add_product,
        create_purchase,
        dashboard,
        initialize_database,
        list_expenses,
        list_products,
        list_purchases,
    )
except ImportError:  # запуск командой: python src/main.py
    from database import (
        DEFAULT_DB_PATH,
        add_product,
        create_purchase,
        dashboard,
        initialize_database,
        list_expenses,
        list_products,
        list_purchases,
    )


def money(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " ₽"


def print_dashboard(db_path: Path) -> None:
    data = dashboard(db_path)
    print("=" * 54)
    print("HomeBudget — учёт домашнего хозяйства")
    print("=" * 54)
    print(f"Активных продуктов: {data['products_count']}")
    print(f"Сохранённых покупок: {data['purchases_count']}")
    print(f"Учтённые расходы: {money(float(data['spent']))}")
    print(f"Позиций на минимальном остатке: {data['low_stock']}")
    print("\nКоманды: products, purchases, expenses, add-product, add-purchase, init")
    print("Подробная справка: python src/main.py --help")


def print_products(db_path: Path) -> None:
    rows = list_products(db_path)
    print("ID | Продукт | Категория | Остаток | Мин. остаток")
    print("-" * 78)
    for row in rows:
        status = " (неактивен)" if not row["is_active"] else ""
        print(
            f"{row['product_id']} | {row['name']}{status} | {row['category']} | "
            f"{row['quantity_on_hand']:g} {row['unit']} | {row['min_quantity']:g} {row['unit']}"
        )
    if not rows:
        print("Список продуктов пуст.")


def print_purchases(db_path: Path) -> None:
    rows = list_purchases(db_path)
    print("ID | Дата | Магазин | Позиций | Сумма по позициям | Записанный расход")
    print("-" * 100)
    for row in rows:
        print(
            f"{row['purchase_id']} | {row['purchase_date']} | {row['store']} | "
            f"{row['item_count']} | {money(float(row['calculated_total']))} | "
            f"{money(float(row['recorded_total'] or 0))}"
        )
    if not rows:
        print("История покупок пуста.")


def print_expenses(db_path: Path) -> None:
    rows = list_expenses(db_path)
    print("ID | Дата | Магазин | Сумма | Описание")
    print("-" * 78)
    for row in rows:
        print(
            f"{row['expense_id']} | {row['expense_date']} | {row['store']} | "
            f"{money(float(row['amount']))} | {row['description'] or ''}"
        )
    print(f"Итого: {money(sum(float(row['amount']) for row in rows))}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="HomeBudget — демонстрационное приложение для учёта продуктов, покупок и расходов."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Путь к файлу SQLite")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Создать структуру БД и добавить демонстрационные данные")
    sub.add_parser("products", help="Показать продукты и остатки")
    sub.add_parser("purchases", help="Показать историю покупок")
    sub.add_parser("expenses", help="Показать список расходов и итог")

    product_parser = sub.add_parser("add-product", help="Добавить продукт")
    product_parser.add_argument("--name", required=True, help="Название продукта")
    product_parser.add_argument("--category", required=True, help="Категория")
    product_parser.add_argument("--unit", required=True, help="Единица измерения, например шт. или кг")
    product_parser.add_argument("--quantity", type=float, default=0, help="Текущий остаток")
    product_parser.add_argument("--min-quantity", type=float, default=0, help="Минимальный остаток")

    purchase_parser = sub.add_parser("add-purchase", help="Записать покупку")
    purchase_parser.add_argument("--store", required=True, help="Магазин")
    purchase_parser.add_argument(
        "--item", action="append", required=True, metavar="ID:QTY:PRICE",
        help="Позиция покупки; аргумент можно повторять, например --item 1:2:89.90",
    )
    purchase_parser.add_argument("--user-id", type=int, default=1, help="ID пользователя (по умолчанию 1)")
    purchase_parser.add_argument("--date", help="Дата в формате ГГГГ-ММ-ДД; по умолчанию текущая")
    purchase_parser.add_argument("--note", default="", help="Комментарий к покупке")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    db_path: Path = args.db
    initialize_database(db_path)

    try:
        if args.command is None:
            print_dashboard(db_path)
        elif args.command == "init":
            print(f"База данных готова: {db_path}")
        elif args.command == "products":
            print_products(db_path)
        elif args.command == "purchases":
            print_purchases(db_path)
        elif args.command == "expenses":
            print_expenses(db_path)
        elif args.command == "add-product":
            new_id = add_product(
                args.name, args.category, args.unit, args.quantity, args.min_quantity, db_path
            )
            print(f"Продукт добавлен. ID: {new_id}")
        elif args.command == "add-purchase":
            parsed_items: list[tuple[int, float, float]] = []
            for item in args.item:
                parts = item.split(":")
                if len(parts) != 3:
                    parser.error(f"Неверный формат позиции {item!r}; ожидается ID:QTY:PRICE")
                parsed_items.append((int(parts[0]), float(parts[1]), float(parts[2])))
            purchase_id, total = create_purchase(
                args.user_id, args.store, parsed_items, args.date, args.note, db_path
            )
            print(f"Покупка №{purchase_id} сохранена. Учтённый расход: {money(total)}")
        else:
            parser.error("Неизвестная команда")
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Ошибка: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
