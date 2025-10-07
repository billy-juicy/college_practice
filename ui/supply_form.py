import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL

class SupplyFormWindow(tk.Toplevel):
    def __init__(self, master, supply_id=None, on_save=None):
        super().__init__(master)
        self.supply_id = supply_id
        self.on_save = on_save
        self.title("Добавить поставку" if supply_id is None else "Редактировать поставку")
        self.geometry("500x500")
        self.resizable(False, False)
        self.configure(bg=DEFAULT_BG)

        self.fields = {}

        # --- Загрузка материалов и сотрудников ---
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM materials")
        materials = cur.fetchall()
        cur.execute("SELECT id, full_name FROM employees")
        employees = cur.fetchall()
        conn.close()

        # --- Поля формы ---
        labels = [
            ("Материал", "material_id"),
            ("Поставщик", "supplier_name"),
            ("Количество", "quantity"),
            ("Цена за единицу", "cost_per_unit"),
            ("Дата поставки (YYYY-MM-DD)", "supply_date"),
            ("Сотрудник", "employee_id")
        ]

        for i, (label_text, field_name) in enumerate(labels):
            tk.Label(self, text=label_text, bg=DEFAULT_BG, font=FONT_SMALL).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if field_name == "material_id":
                cb = ttk.Combobox(self, values=[f"{m[0]} — {m[1]}" for m in materials], state="readonly", font=FONT_SMALL)
                cb.grid(row=i, column=1, padx=10, pady=5)
                self.fields[field_name] = cb
            elif field_name == "employee_id":
                cb = ttk.Combobox(self, values=[f"{e[0]} — {e[1]}" for e in employees], state="readonly", font=FONT_SMALL)
                cb.grid(row=i, column=1, padx=10, pady=5)
                self.fields[field_name] = cb
            else:
                entry = tk.Entry(self, width=40, font=FONT_SMALL)
                entry.grid(row=i, column=1, padx=10, pady=5)
                self.fields[field_name] = entry

        # --- Кнопки ---
        button_frame = tk.Frame(self, bg=DEFAULT_BG)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Сохранить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.save_supply).pack(side="left", padx=5)
        tk.Button(button_frame, text="Отмена", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.destroy).pack(side="left", padx=5)

        if self.supply_id:
            self.load_supply_data()

    def load_supply_data(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT material_id, supplier_name, quantity, cost_per_unit, supply_date, employee_id
            FROM supplier_materials WHERE id=?
        """, (self.supply_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Ошибка", "Поставка не найдена")
            self.destroy()
            return

        for key, val in zip(self.fields.keys(), row):
            field = self.fields[key]
            if isinstance(field, ttk.Combobox):
                field.set(str(val))
            else:
                field.insert(0, val)

    def validate_fields(self):
        data = {}
        for key, widget in self.fields.items():
            value = widget.get().strip()
            if key in ["quantity", "cost_per_unit"]:
                try:
                    value = float(value)
                except ValueError:
                    messagebox.showwarning("Ошибка", f"Поле '{key}' должно быть числом")
                    return None
            data[key] = value

        required = ["material_id", "supplier_name", "quantity", "cost_per_unit", "supply_date", "employee_id"]
        for key in required:
            if not data[key]:
                messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно")
                return None

        # Получаем id из комбобоксов
        data["material_id"] = int(data["material_id"].split(" — ")[0])
        data["employee_id"] = int(data["employee_id"].split(" — ")[0])

        return data

    def save_supply(self):
        data = self.validate_fields()
        if not data:
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            if self.supply_id:
                cur.execute("""
                    UPDATE supplier_materials
                    SET material_id=?, supplier_name=?, quantity=?, cost_per_unit=?, supply_date=?, employee_id=?
                    WHERE id=?
                """, (*data.values(), self.supply_id))
            else:
                cur.execute("""
                    INSERT INTO supplier_materials (material_id, supplier_name, quantity, cost_per_unit, supply_date, employee_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, tuple(data.values()))

            conn.commit()
            messagebox.showinfo("Успех", "Поставка сохранена")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
        finally:
            conn.close()
