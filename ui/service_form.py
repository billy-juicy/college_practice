import tkinter as tk
from tkinter import messagebox
from logic.db_utils import get_connection


class ServiceFormWindow(tk.Toplevel):
    def __init__(self, master, service_id=None, on_save=None):
        super().__init__(master)
        self.service_id = service_id
        self.on_save = on_save
        self.title("Добавить услугу" if service_id is None else "Редактировать услугу")
        self.geometry("500x550")
        self.resizable(False, False)

        # --- Поля формы ---
        self.fields = {}
        labels = [
            ("Код услуги", "code"),
            ("Название", "name"),
            ("Тип", "type"),
            ("Описание", "description"),
            ("Минимальная стоимость", "min_cost"),
            ("Норма времени (мин)", "time_norm"),
            ("Расчётная стоимость", "estimated_cost"),
            ("Номер цеха", "workshop_number"),
            ("Количество персонала", "staff_count")
        ]

        for i, (label, field) in enumerate(labels):
            tk.Label(self, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(self, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.fields[field] = entry

        # Кнопки
        tk.Button(self, text="Сохранить", command=self.save_service).grid(row=len(labels), column=0, pady=15)
        tk.Button(self, text="Отмена", command=self.destroy).grid(row=len(labels), column=1, pady=15)

        # Если редактирование
        if self.service_id:
            self.load_service_data()

    def load_service_data(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT code, name, type, description, min_cost,
                   time_norm, estimated_cost, workshop_number, staff_count
            FROM services WHERE id=?
        """, (self.service_id,))
        service = cur.fetchone()
        conn.close()

        if not service:
            messagebox.showerror("Ошибка", "Услуга не найдена")
            self.destroy()
            return

        for key, value in zip(self.fields.keys(), service):
            if value is not None:
                self.fields[key].insert(0, value)

    def validate_fields(self):
        data = {key: self.fields[key].get().strip() for key in self.fields}

        # Проверка обязательных
        for key in ["code", "name", "type", "min_cost"]:
            if not data[key]:
                messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно")
                return None

        # Проверка числовых полей
        numeric_fields = ["min_cost", "time_norm", "estimated_cost", "workshop_number", "staff_count"]
        for key in numeric_fields:
            if data[key]:
                try:
                    data[key] = float(data[key])
                except ValueError:
                    messagebox.showwarning("Ошибка", f"Поле '{key}' должно быть числом")
                    return None
            else:
                data[key] = None

        return data

    def save_service(self):
        data = self.validate_fields()
        if not data:
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            if self.service_id:
                cur.execute("""
                    UPDATE services
                    SET code=?, name=?, type=?, description=?, min_cost=?,
                        time_norm=?, estimated_cost=?, workshop_number=?, staff_count=?
                    WHERE id=?
                """, (*data.values(), self.service_id))
            else:
                cur.execute("""
                    INSERT INTO services (code, name, type, description, min_cost,
                                          time_norm, estimated_cost, workshop_number, staff_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(data.values()))

            conn.commit()
            messagebox.showinfo("Успех", "Данные услуги сохранены")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
        finally:
            conn.close()
