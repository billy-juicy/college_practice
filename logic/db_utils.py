import sqlite3
import os

# Пути к файлам БД и SQL-скрипта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "clean_planet.db")
INIT_SQL_PATH = os.path.join(BASE_DIR, "db", "init_db.sql")


def get_connection():
    """Возвращает соединение с SQLite базой."""
    return sqlite3.connect(DB_PATH)


def init_database():
    """Инициализирует базу данных, если таблицы ещё не созданы."""
    conn = get_connection()
    cur = conn.cursor()

    # Проверяем наличие таблицы employees
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    if not cur.fetchone():
        if not os.path.exists(INIT_SQL_PATH):
            raise FileNotFoundError(f"SQL файл для инициализации базы не найден: {INIT_SQL_PATH}")
        with open(INIT_SQL_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        print("База данных успешно создана/обновлена.")
    conn.commit()
    conn.close()
