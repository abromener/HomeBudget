INSERT OR IGNORE INTO users (user_id, username, full_name, role) VALUES
    (1, 'home_user', 'Домашний пользователь', 'user'),
    (2, 'admin', 'Администратор системы', 'admin');

INSERT OR IGNORE INTO categories (category_id, name, description) VALUES
    (1, 'Молочные продукты', 'Молоко, йогурты и другие молочные продукты'),
    (2, 'Овощи и фрукты', 'Свежие овощи, фрукты и ягоды'),
    (3, 'Бакалея', 'Крупы и продукты длительного хранения'),
    (4, 'Хлебобулочные изделия', 'Хлеб и выпечка'),
    (5, 'Бытовая химия', 'Средства для уборки и ухода за домом');

INSERT OR IGNORE INTO products
    (product_id, name, category_id, unit, quantity_on_hand, min_quantity, is_active) VALUES
    (1, 'Молоко 1 л', 1, 'шт.', 2, 1, 1),
    (2, 'Яблоки', 2, 'кг', 1.5, 1, 1),
    (3, 'Гречка', 3, 'упак.', 1, 1, 1),
    (4, 'Хлеб', 4, 'шт.', 2, 1, 1),
    (5, 'Средство для посуды', 5, 'шт.', 1, 1, 1),
    (6, 'Йогурт', 1, 'шт.', 3, 2, 1);

INSERT OR IGNORE INTO purchases (purchase_id, user_id, purchase_date, store, note) VALUES
    (1, 1, '2026-10-20', 'Магнит', 'Покупка продуктов на неделю'),
    (2, 1, '2026-10-21', 'Пятёрочка', 'Небольшая дополнительная покупка');

INSERT OR IGNORE INTO purchase_items (item_id, purchase_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 2, 89.90),
    (2, 1, 2, 1.2, 119.50),
    (3, 2, 4, 2, 45.00),
    (4, 2, 3, 1, 79.90);

INSERT OR IGNORE INTO expenses (expense_id, purchase_id, amount, expense_date, description) VALUES
    (1, 1, 323.20, '2026-10-20', 'Расходы по покупке в Магните'),
    (2, 2, 169.90, '2026-10-21', 'Расходы по покупке в Пятёрочке');
