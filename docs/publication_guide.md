# Памятка к лабораторным работам №2 и №3

## 1. Что открыть на защите

1. `README.md` — описание проекта и изображения диаграмм.
2. `diagrams/use_case.puml` — исходный текст Use Case диаграммы в PlantUML.
3. `diagrams/er_diagram.puml` — исходный текст ER-модели.
4. `database/schema.sql` — создание таблиц, первичные и внешние ключи, ограничения.
5. `database/homebudget.db` — готовую базу в DB Browser for SQLite или SQLiteStudio.
6. `src/main.py` и `src/database.py` — программу и слой доступа к данным.

## 2. Проверка программы

Из корневой папки:

```bash
python src/main.py
python src/main.py products
python src/main.py purchases
python src/main.py expenses
python -m unittest discover -s tests -v
```

Ожидается, что сводка показывает 6 активных продуктов, 2 сохранённые покупки и общие расходы 493,10 ₽. Для списка продуктов отображаются категория, количество и минимальный остаток.

## 3. Как открыть базу данных

1. Запустите DB Browser for SQLite или SQLiteStudio.
2. Выберите `database/homebudget.db`.
3. Откройте таблицы `users`, `categories`, `products`, `purchases`, `purchase_items`, `expenses`.
4. В SQL-редакторе можно выполнить, например:

   ```sql
   SELECT p.name, c.name AS category, p.quantity_on_hand, p.unit
   FROM products AS p
   JOIN categories AS c ON c.category_id = p.category_id
   ORDER BY c.name, p.name;

   SELECT purchase_date, store, amount
   FROM purchases
   JOIN expenses USING (purchase_id)
   ORDER BY purchase_date;
   ```

## 4. Публикация на GitHub

Локальный каталог уже является Git-репозиторием с коммитами. На GitHub создайте пустой репозиторий и выполните `git remote add origin https://github.com/ВАШ_ЛОГИН/HomeBudget.git`, а затем `git push -u origin main`. Замените адрес на URL своего репозитория. В отчётах не указывается выдуманная ссылка: её можно вписать после публикации.

## 5. Что нужно сделать на собственном компьютере

- Если вы работаете в VS Code, установите расширения **Git** (встроенные средства контроля версий), **Markdown All in One** и **PlantUML**. Для PlantUML в локальном режиме понадобится Java и Graphviz; следуйте инструкции расширения.
- Укажите настоящее имя и адрес электронной почты командой `git config user.name` и `git config user.email`.
- Подключите свой удалённый репозиторий GitHub и выполните `git push`.
- Для отчёта о рабочей среде сделайте собственные скриншоты VS Code с установленными расширениями, вывода `python src/main.py`, дерева файлов и страницы GitHub. Из этого архива нельзя достоверно показать состояние программ, установленных на вашем компьютере.
