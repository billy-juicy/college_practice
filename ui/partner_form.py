import tkinter as tk
from tkinter import ttk, messagebox
import re
from logic.db_utils import get_connection

class PartnerFormWindow(tk.Toplevel):
    def __init__(self, master, partner_id=None, on_save=None):
        super().__init__(master)
        self.partner_id = partner_id  # None — добавление, иначе редактирование
        self.on_save = on_save
        self.title("Добавить партнёра" if partner_id is None else "Редактировать партнёра")
        self.geometry("450x450")
        self.resizable(False, False)

        # --- Поля формы ---
        self.fields = {}

        labels = [
            ("Наименование", "name"),
            ("Тип партнёра", "type"),
            ("Рейтинг (целое ≥0)", "rating"),
            ("Юридический адрес", "legal_address"),
            ("ИНН", "inn"),
            ("ФИО руководителя", "director_name"),
            ("Телефон (+7XXXXXXXXXX)", "phone"),
            ("Email", "email"),
            ("URL логотипа (необязательно)", "logo_url")
        ]

        for idx, (label_text, field_name) in enumerate(labels):
            tk.Label(self, text=label_text).grid(row=idx, column=0, sticky="w", padx=10, pady=5)
            if field_name == "type":
                self.fields[field_name] = ttk.Combobox(self, values=["Пункт приёма-выдачи", "Корпоративный клиент"], state="readonly")
                self.fields[field_name].grid(row=idx, column=1, padx=10, pady=5)
            else:
                self.fields[field_name] = tk.Entry(self)
                self.fields[field_name].grid(row=idx, column=1, padx=10, pady=5)

        # Кнопки
        tk.Button(self, text="Сохранить", command=self.save_partner).grid(row=len(labels), column=0, pady=15)
        tk.Button(self, text="Отмена", command=self.destroy).grid(row=len(labels), column=1, pady=15)
        tk.Button(self, text="Удалить", command=self.delete_partner).grid(row=len(labels), column=2, pady=15)

        # Если редактирование — загрузка данных из базы
        if self.partner_id:
            self.load_partner_data()

    def load_partner_data(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT name, type, rating, legal_address, inn, director_name, phone, email, logo_url 
            FROM partners WHERE id=?""",
                    (self.partner_id,))
        partner = cur.fetchone()
        conn.close()
        if not partner:
            messagebox.showerror("Ошибка", "Партнёр не найден")
            self.destroy()
            return
        for idx, key in enumerate(["name", "type", "rating", "legal_address", "inn", "director_name", "phone", "email", "logo_url"]):
            if partner[idx] is not None:
                self.fields[key].insert(0, partner[idx])

    def validate_fields(self):
        data = {}
        for key in ["name", "type", "rating", "legal_address", "inn", "director_name", "phone", "email", "logo_url"]:
            data[key] = self.fields[key].get().strip()

        # Обязательные поля
        for key in ["name", "type", "rating", "legal_address", "inn", "director_name", "phone", "email"]:
            if not data[key]:
                messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно")
                return None

        # Проверка рейтинга
        if not data["rating"].isdigit() or int(data["rating"]) < 0:
            messagebox.showwarning("Ошибка", "Рейтинг должен быть целым числом ≥0")
            return None
        data["rating"] = int(data["rating"])

        # Проверка телефона
        if not re.fullmatch(r"\+7\d{10}", data["phone"]):
            messagebox.showwarning("Ошибка", "Телефон должен быть в формате +7XXXXXXXXXX")
            return None

        # Проверка email
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            messagebox.showwarning("Ошибка", "Некорректный email")
            return None

        return data

    def save_partner(self):
        data = self.validate_fields()
        if not data:
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            if self.partner_id:
                cur.execute("""
                    UPDATE partners
                    SET name=?, type=?, rating=?, legal_address=?, inn=?, director_name=?, phone=?, email=?, logo_url=?
                    WHERE id=?
                """, (*data.values(), self.partner_id))
            else:
                cur.execute("""
                    INSERT INTO partners (name, type, rating, legal_address, inn, director_name, phone, email, logo_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(data.values()))
            conn.commit()
            messagebox.showinfo("Успех", "Данные успешно сохранены")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
        finally:
            conn.close()

