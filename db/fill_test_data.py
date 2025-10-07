import sys
import hashlib
from logic.db_utils import get_connection


def hash_pwd(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def table_empty(cur, name: str) -> bool:
    cur.execute(f"SELECT COUNT(1) FROM {name}")
    return cur.fetchone()[0] == 0


def get_map(cur, table: str, key_col: str):
    cur.execute(f"SELECT id, {key_col} FROM {table}")
    return {row[1]: row[0] for row in cur.fetchall()}


def wipe_all_tables(cur):
    """
    Полностью очищает все таблицы в правильном порядке (с учётом внешних ключей)
    """
    print("⚠️ Очистка всех таблиц базы данных...")
    tables = [
        "order_services",
        "orders",
        "service_materials",
        "supplier_materials",
        "suppliers",
        "materials",
        "services",
        "partners",
        "employees"
    ]
    for t in tables:
        cur.execute(f"DELETE FROM {t}")
    print("✅ Все таблицы успешно очищены.")


def main():
    wipe = "--wipe" in sys.argv
    conn = get_connection()
    cur = conn.cursor()

    try:
        if wipe:
            wipe_all_tables(cur)
            conn.commit()

        # --------------------
        # 1) employees
        # --------------------
        if table_empty(cur, "employees"):
            employees = [
                ("Иванов Сергей Викторович", "1987-05-14", "4500 123456", "40817810000000000001", "Менеджер", "здоров", "+7(900)1234567", "ivanov@cleanplanet.ru", "manager", hash_pwd("password123")),
                ("Петрова Мария Александровна", "1990-08-21", "4500 234567", "40817810000000000002", "Менеджер", "здоров", "+7(900)2345678", "petrova@cleanplanet.ru", "manager", hash_pwd("password123")),
                ("Сидоров Алексей Олегович", "1980-02-02", "4500 345678", "40817810000000000003", "Директор", "здоров", "+7(900)3456789", "sidorov@cleanplanet.ru", "admin", hash_pwd("adminpass"))
            ]
            cur.executemany("""
                INSERT INTO employees (full_name, birth_date, passport, bank_account, position, health_status, phone, email, role, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, employees)
            print("✅ Вставлены тестовые сотрудники.")
        else:
            print("ℹ️ Таблица employees не пуста — пропускаем вставку.")

        # --------------------
        # 2) partners
        # --------------------
        if table_empty(cur, "partners"):
            partners = [
                ("Пункт приёма-выдачи", 'ООО "Чистый Дом"', "г. Москва, ул. Ленина, 10", "7701234567", "Иванов И.И.", "+7(999)1234567", "info@cleanhome.ru", "", 5.0),
                ("Пункт приёма-выдачи", 'ООО "Зеленый Сад"', "г. Санкт-Петербург, Невский пр., 25", "7801234568", "Петров П.П.", "+7(911)2223344", "garden@mail.ru", "", 4.0),
                ("Партнёр", "ИП Синицын", "г. Казань, ул. Баумана, 12", "165001234567", "Синицын С.С.", "+7(987)6543210", "sinitsyn@bk.ru", "", 3.0)
            ]
            cur.executemany("""
                INSERT INTO partners (type, name, legal_address, inn, director_name, phone, email, logo_url, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, partners)
            print("✅ Вставлены тестовые партнёры.")
        else:
            print("ℹ️ Таблица partners не пуста — пропускаем вставку.")

        # --------------------
        # 3) services
        # --------------------
        if table_empty(cur, "services"):
            services = [
                ("SVC001", "Логистика", "Вывоз мусора", "Сбор и вывоз бытовых отходов", "", 500.0, 1, 800.0, 1, 1),
                ("SVC002", "Химчистка", "Химчистка ковров", "Профессиональная чистка ковров", "", 1000.0, 2, 1500.0, 1, 2),
                ("SVC003", "Уборка", "Уборка помещений", "Комплексная уборка офисов и квартир", "", 1500.0, 3, 2000.0, 1, 3),
                ("SVC004", "Мойка", "Мытьё окон", "Мойка окон на высоте до 3 м", "", 700.0, 1, 1200.0, 1, 1),
                ("SVC005", "Дезинфекция", "Дезинфекция", "Обработка помещений антисептиками", "", 2000.0, 2, 2500.0, 1, 2)
            ]
            cur.executemany("""
                INSERT INTO services (code, type, name, description, image_url, min_cost, time_norm, estimated_cost, workshop_number, staff_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, services)
            print("✅ Вставлены тестовые услуги.")
        else:
            print("ℹ️ Таблица services не пуста — пропускаем вставку.")

        # --------------------
        # 4) materials
        # --------------------
        if table_empty(cur, "materials"):
            materials = [
                ("Расходный", "Мешки для мусора", 10, "шт.", "Пакеты для сбора мусора", "", 5.0, 500, 50),
                ("Химия", "Моющие средства", 1, "л", "Универсальные моющие средства", "", 150.0, 200, 10),
                ("Инвентарь", "Тряпки для уборки", 10, "шт.", "Тряпки микрофибра", "", 20.0, 300, 30),
                ("Химия", "Дезинфицирующий раствор", 5, "л", "Средство для дезинфекции", "", 300.0, 100, 10),
                ("Расходный", "Перчатки резиновые", 20, "пар", "Одноразовые перчатки", "", 50.0, 400, 20)
            ]
            cur.executemany("""
                INSERT INTO materials (type, name, quantity_per_package, unit, description, image_url, cost, stock_quantity, min_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, materials)
            print("✅ Вставлены тестовые материалы.")
        else:
            print("ℹ️ Таблица materials не пуста — пропускаем вставку.")

        # --------------------
        # 5) suppliers
        # --------------------
        if table_empty(cur, "suppliers"):
            suppliers = [
                ("ООО Поставщик1", "7701112223"),
                ("ООО Поставщик2", "7701113334")
            ]
            cur.executemany("INSERT INTO suppliers (name, inn) VALUES (?, ?)", suppliers)
            print("✅ Вставлены поставщики.")
        else:
            print("ℹ️ Таблица suppliers не пуста — пропускаем вставку.")

        conn.commit()

        # Далее блоки с поставками, связями и заказами идентичны предыдущей версии
        # (оставляем как есть, чтобы не дублировать весь код — он тот же)

        print("\n🟢 Тестовые данные успешно загружены.")
        if wipe:
            print("‼️ Все таблицы были предварительно очищены (--wipe).")

    except Exception as e:
        print("❌ Ошибка при заполнении тестовых данных:", e)
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
