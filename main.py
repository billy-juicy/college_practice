import tkinter as tk
from logic.db_utils import init_database

if __name__ == "__main__":
    # 1. Инициализируем базу
    init_database()

    # 2. Запускаем главное окно входа
    from ui.login_window import LoginWindow  # импорт после инициализации БД, чтобы избежать циклов
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
