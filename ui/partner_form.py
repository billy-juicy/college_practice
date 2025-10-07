import tkinter as tk
from tkinter import ttk, messagebox
import re
from logic.db_utils import get_connection
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL


class PartnerFormWindow(tk.Toplevel):
    def __init__(self, master, partner_id=None, on_save=None):
        super().__init__(master)
        self.partner_id = partner_id  # None — добавление, иначе редактирование
        self.on_save = on_save
        self.title("Добавить партнёра" if partner_id is None else "Редактировать партнёра")
        self.geometry("450x450")
        self.resizable(False, False)
        self.configure(bg=DEFAULT_BG)

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
            tk.Label(self, text=label_text, bg=DEFAULT_BG, font=FONT_SMALL).grid(
                row=idx, column=0, sticky="w", padx=10, pady=5
            )
            if field_name == "type":
                self.fields[field_name] = ttk.Combobox(
                    self, values=["Пункт приёма-выдачи", "Корпоративный клиент"], state="readonly", font=FONT_SMALL
                )
                self.fields[field_name].grid(row=idx, column=1, padx=10, pady=5)
            else:
                self.fields[field_name] = tk.Entry(self, font=FONT_SMALL)
                self.fields[field_name].grid(row=idx, column=1, padx=10, pady=5)

        # --- Панель кнопок ---
        button_frame = tk.Frame(self, bg=DEFAULT_BG)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Сохранить", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.save_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="Отмена", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.destroy).pack(side="left", padx=5)

        # Если редактирование — загрузка данных из базы
        if self.partner_id:
            self.load_partner_data()

    def load_partner_data(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT name, type, rating, legal_address, inn, director_name, phone, email, logo_url 
            FROM partners WHERE id=?""", (self.partner_id,))
        partner = cur.fetchone()
        conn.close()
        if not partner:
            messagebox.showerror("Ошибка", "Партнёр не найден")
            self.destroy()
            return
        for idx, key in enumerate(
                ["name", "type", "rating", "legal_address", "inn", "director_name", "phone", "email", "logo_url"]):
            if partner[idx] is not None:
                if isinstance(self.fields[key], ttk.Combobox):
                    self.fields[key].set(partner[idx])
                else:
                    self.fields[key].delete(0, tk.END)
                    self.fields[key].insert(0, partner[idx])

    def validate_fields(self):
        data = {key: self.fields[key].get().strip() for key in self.fields}

        # Обязательные поля
        for key in ["name", "type", "rating", "legal_address", "inn", "director_name", "phone", "email"]:
            if not data[key]:
                messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно")
                return None

        # Рейтинг
        if not data["rating"].isdigit() or int(data["rating"]) < 0:
            messagebox.showwarning("Ошибка", "Рейтинг должен быть целым числом ≥0")
            return None
        data["rating"] = int(data["rating"])

        # Телефон
        if not re.fullmatch(r"\+7\d{10}", data["phone"]):
            messagebox.showwarning("Ошибка", "Телефон должен быть в формате +7XXXXXXXXXX")
            return None

        # Email
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
