import tkinter as tk
from tkinter import messagebox
from logic.db_utils import get_connection


class MaterialFormWindow(tk.Toplevel):
    def __init__(self, master, material_id=None, on_save=None):
        super().__init__(master)
        self.material_id = material_id
        self.on_save = on_save
        self.title("Добавить материал" if material_id is None else "Редактировать материал")
        self.geometry("550x550")
        self.resizable(False, False)

        # --- Поля формы ---
        self.fields = {}
        labels = [
            ("Тип", "type"),
            ("Название", "name"),
            ("Кол-во в упаковке", "quantity_per_package"),
            ("Ед. изм.", "unit"),
            ("Описание", "description"),
            ("URL изображения", "image_url"),
            ("Стоимость", "cost"),
            ("Количество на складе", "stock_quantity"),
            ("Минимальный запас", "min_stock")
        ]

        for i, (label, field) in enumerate(labels):
            tk.Label(self, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(self, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.fields[field] = entry

        # Кнопки
        tk.Button(self, text="Сохранить", command=self.save_material).grid(row=len(labels), column=0, pady=15)
        tk.Button(self, text="Отмена", command=self.destroy).grid(row=len(labels), column=1, pady=15)

        # Если редактирование
        if self.material_id:
            self.load_material_data()

    def load_material_data(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT type, name, quantity_per_package, unit, description,
                   image_url, cost, stock_quantity, min_stock
            FROM materials WHERE id=?
        """, (self.material_id,))
        material = cur.fetchone()
        conn.close()

        if not material:
            messagebox.showerror("Ошибка", "Материал не найден")
            self.destroy()
            return

        for key, value in zip(self.fields.keys(), material):
            if value is not None:
                self.fields[key].insert(0, value)

    def validate_fields(self):
        data = {key: self.fields[key].get().strip() for key in self.fields}

        # Проверка обязательных
        for key in ["name", "type", "cost"]:
            if not data[key]:
                messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно")
                return None

        # Проверка числовых
        numeric_fields = ["quantity_per_package", "cost", "stock_quantity", "min_stock"]
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

    def save_material(self):
        data = self.validate_fields()
        if not data:
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            if self.material_id:
                cur.execute("""
                    UPDATE materials
                    SET type=?, name=?, quantity_per_package=?, unit=?, description=?,
                        image_url=?, cost=?, stock_quantity=?, min_stock=?
                    WHERE id=?
                """, (*data.values(), self.material_id))
            else:
                cur.execute("""
                    INSERT INTO materials (type, name, quantity_per_package, unit, description,
                                           image_url, cost, stock_quantity, min_stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(data.values()))

            conn.commit()
            messagebox.showinfo("Успех", "Данные сохранены")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
        finally:
            conn.close()
