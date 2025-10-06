import tkinter as tk
from tkinter import messagebox
import hashlib
import re
from logic.db_utils import get_connection

class RegisterWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Регистрация — Чистая планета")
        self.master.geometry("400x650")

        # Поля регистрации
        self.fields = {}
        labels = [
            ("ФИО", "full_name"),
            ("Дата рождения (YYYY-MM-DD)", "birth_date"),
            ("Паспорт", "passport"),
            ("Банковский счёт", "bank_account"),
            ("Должность", "position"),
            ("Состояние здоровья", "health_status"),
            ("Телефон (+7XXXXXXXXXX)", "phone"),
            ("Email", "email"),
            ("Роль (admin/manager)", "role"),
            ("Пароль", "password")
        ]

        for text, key in labels:
            tk.Label(master, text=text).pack(pady=3)
            entry = tk.Entry(master, width=30, show="*" if key=="password" else None)
            entry.pack()
            self.fields[key] = entry

        # Кнопки
        tk.Button(master, text="Зарегистрироваться", command=self.register).pack(pady=10)
        tk.Button(master, text="Назад", command=self.back_to_login).pack()

    def validate_fields(self, data):
        # Проверка ФИО — должно быть хотя бы два слова
        if not re.match(r"^[А-Яа-яЁёA-Za-z\s\-]{3,}$", data["full_name"]) or len(data["full_name"].split()) < 2:
            return "Введите корректное ФИО (Фамилия Имя)"

        # Дата рождения — YYYY-MM-DD
        if data["birth_date"] and not re.match(r"^\d{4}-\d{2}-\d{2}$", data["birth_date"]):
            return "Введите дату рождения в формате YYYY-MM-DD"

        # Паспорт — 10 цифр
        if data["passport"] and not re.match(r"^\d{10}$", data["passport"]):
            return "Введите паспорт корректно (10 цифр)"

        # Банковский счёт — 20 цифр
        if data["bank_account"] and not re.match(r"^\d{20}$", data["bank_account"]):
            return "Введите банковский счёт корректно (20 цифр)"

        # Телефон — +7XXXXXXXXXX
        if data["phone"] and not re.match(r"^\+7\d{10}$", data["phone"]):
            return "Введите телефон в формате +7XXXXXXXXXX"

        # Email — простой шаблон
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", data["email"]):
            return "Введите корректный email"

        # Роль — только admin или manager
        if data["role"].lower() not in ["admin", "manager"]:
            return "Роль должна быть 'admin' или 'manager'"

        return None  # Всё корректно

    def register(self):
        # Сбор данных
        data = {k: v.get().strip() for k, v in self.fields.items()}

        # Проверка обязательных полей
        mandatory = ["full_name", "email", "password", "role"]
        if any(not data[m] for m in mandatory):
            messagebox.showwarning("Ошибка", "Обязательные поля не заполнены")
            return

        # Валидация
        error = self.validate_fields(data)
        if error:
            messagebox.showerror("Ошибка ввода", error)
            return

        # Хешируем пароль
        data["password"] = hashlib.sha256(data["password"].encode()).hexdigest()

        try:
            conn = get_connection()
            cur = conn.cursor()

            # Проверка уникальности email
            cur.execute("SELECT id FROM employees WHERE email=?", (data["email"],))
            if cur.fetchone():
                messagebox.showerror("Ошибка", "Такой email уже зарегистрирован")
                return

            # Сохранение в базу
            cur.execute("""
                INSERT INTO employees 
                (full_name, birth_date, passport, bank_account, position, health_status, phone, email, role, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["full_name"], data["birth_date"], data["passport"], data["bank_account"],
                data["position"], data["health_status"], data["phone"], data["email"],
                data["role"].lower(), data["password"]
            ))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при работе с базой: {e}")
            return
        finally:
            conn.close()

        messagebox.showinfo("Успешно", "Регистрация завершена")
        self.back_to_login()

    def back_to_login(self):
        self.master.destroy()
        import ui.login_window as login_module
        root = tk.Tk()
        login_module.LoginWindow(root)
        root.mainloop()
