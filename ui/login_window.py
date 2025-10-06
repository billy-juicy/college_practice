import tkinter as tk
from tkinter import messagebox
import hashlib
from logic.db_utils import get_connection

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Чистая планета — Вход")
        self.master.geometry("400x300")

        # Email
        tk.Label(master, text="Email:").pack(pady=5)
        self.email_entry = tk.Entry(master, width=30)
        self.email_entry.pack()

        # Пароль
        tk.Label(master, text="Пароль:").pack(pady=5)
        self.password_entry = tk.Entry(master, show="*", width=30)
        self.password_entry.pack()

        # Кнопки
        tk.Button(master, text="Войти", command=self.login).pack(pady=10)
        tk.Button(master, text="Регистрация", command=self.open_register).pack()

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Ошибка", "Введите email и пароль")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, full_name, role, password FROM employees WHERE email=?", (email,))
            user = cur.fetchone()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обращении к базе: {e}")
            return
        finally:
            conn.close()

        if not user:
            messagebox.showerror("Ошибка", "Пользователь не найден")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()
        if user[3] != hashed:
            messagebox.showerror("Ошибка", "Неверный пароль")
            return

        # Успешный вход — переход на MainWindow
        self.master.destroy()
        import ui.main_window as main_module
        root = tk.Tk()
        main_module.MainWindow(root, user)
        root.mainloop()

    def open_register(self):
        # Переход на окно регистрации
        self.master.destroy()
        import ui.register_window as reg_module
        root = tk.Tk()
        reg_module.RegisterWindow(root)
        root.mainloop()
