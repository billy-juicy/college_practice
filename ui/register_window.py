import tkinter as tk
from tkinter import messagebox
import hashlib
import re
from logic.db_utils import get_connection
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL

class RegisterWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Регистрация — Чистая планета")
        self.master.geometry("400x750")
        self.master.configure(bg=DEFAULT_BG)

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
            tk.Label(master, text=text, bg=DEFAULT_BG, font=FONT_MAIN).pack(pady=5)
            entry = tk.Entry(master, width=30, font=FONT_SMALL, show="*" if key=="password" else None)
            entry.pack(pady=2)
            self.fields[key] = entry

        # --- Панель кнопок ---
        button_frame = tk.Frame(master, bg=DEFAULT_BG)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Зарегистрироваться", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=16, command=self.register).pack(side="left", padx=5)
        tk.Button(button_frame, text="Назад", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=8, command=self.back_to_login).pack(side="left", padx=5)

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
        data = {k: v.get().strip() for k, v in self.fields.items()}

        mandatory = ["full_name", "email", "password", "role"]
        if any(not data[m] for m in mandatory):
            messagebox.showwarning("Ошибка", "Обязательные поля не заполнены")
            return

        error = self.validate_fields(data)
        if error:
            messagebox.showerror("Ошибка ввода", error)
            return

        data["password"] = hashlib.sha256(data["password"].encode()).hexdigest()

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT id FROM employees WHERE email=?", (data["email"],))
            if cur.fetchone():
                messagebox.showerror("Ошибка", "Такой email уже зарегистрирован")
                return

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
