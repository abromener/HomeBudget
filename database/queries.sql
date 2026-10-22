-- 1. Каталог продуктов с названиями категорий
SELECT p.product_id, p.name, c.name AS category,
       p.quantity_on_hand, p.unit, p.min_quantity
FROM products AS p
JOIN categories AS c ON c.category_id = p.category_id
ORDER BY c.name, p.name;

-- 2. Состав каждой покупки и стоимость позиции
SELECT pu.purchase_id, pu.purchase_date, pu.store,
       p.name AS product, pi.quantity, pi.unit_price,
       ROUND(pi.quantity * pi.unit_price, 2) AS line_total
FROM purchases AS pu
JOIN purchase_items AS pi ON pi.purchase_id = pu.purchase_id
JOIN products AS p ON p.product_id = pi.product_id
ORDER BY pu.purchase_id, p.name;

-- 3. Расходы по датам и итоговая сумма
SELECT expense_date, description, amount
FROM expenses
ORDER BY expense_date;

SELECT ROUND(COALESCE(SUM(amount), 0), 2) AS total_expenses
FROM expenses;

-- 4. Проверка ссылочной целостности: в корректной БД результат пуст
PRAGMA foreign_key_check;
