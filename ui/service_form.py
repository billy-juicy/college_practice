import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL


class ServiceFormWindow(tk.Toplevel):
    def __init__(self, master, service_id=None, on_save=None):
        super().__init__(master)
        self.service_id = service_id
        self.on_save = on_save
        self.title("Добавить услугу" if service_id is None else "Редактировать услугу")
        self.geometry("700x650")
        self.resizable(False, False)
        self.configure(bg=DEFAULT_BG)

        # --- Основные поля услуги ---
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

        for i, (label_text, field_name) in enumerate(labels):
            tk.Label(self, text=label_text, bg=DEFAULT_BG, font=FONT_SMALL).grid(
                row=i, column=0, sticky="w", padx=10, pady=5
            )
            self.fields[field_name] = tk.Entry(self, font=FONT_SMALL)
            self.fields[field_name].grid(row=i, column=1, padx=10, pady=5)

        # --- Таблица материалов для услуги ---
        tk.Label(self, text="Материалы для услуги", bg=DEFAULT_BG, font=FONT_MAIN).grid(
            row=len(labels), column=0, columnspan=2, pady=10
        )

        self.materials_tree = ttk.Treeview(self, columns=("material_name", "quantity", "unit"), show="headings", height=8)
        self.materials_tree.heading("material_name", text="Материал")
        self.materials_tree.heading("quantity", text="Количество")
        self.materials_tree.heading("unit", text="Ед. изм.")
        self.materials_tree.grid(row=len(labels)+1, column=0, columnspan=2, padx=10, pady=5)

        # Кнопки управления материалами
        tk.Button(self, text="Добавить материал", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  command=self.add_material).grid(row=len(labels)+2, column=0, pady=5, sticky="e")
        tk.Button(self, text="Удалить материал", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  command=self.remove_material).grid(row=len(labels)+2, column=1, pady=5, sticky="w")

        # --- Панель кнопок сохранения ---
        button_frame = tk.Frame(self, bg=DEFAULT_BG)
        button_frame.grid(row=len(labels)+3, column=0, columnspan=2, pady=15)
        tk.Button(button_frame, text="Сохранить", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.save_service).pack(side="left", padx=5)
        tk.Button(button_frame, text="Отмена", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.destroy).pack(side="left", padx=5)

        self.load_all_materials()
        if self.service_id:
            self.load_service_data()

    # --- Загрузка доступных материалов ---
    def load_all_materials(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, unit FROM materials")
        self.all_materials = cur.fetchall()  # [(id, name, unit), ...]
        conn.close()

    # --- Добавление материала в таблицу ---
    def add_material(self):
        if not self.all_materials:
            messagebox.showwarning("Ошибка", "Сначала добавьте материалы в базу")
            return

        # Простое окно выбора материала
        top = tk.Toplevel(self)
        top.title("Выбрать материал")
        top.geometry("400x200")
        tk.Label(top, text="Материал", font=FONT_SMALL).grid(row=0, column=0, padx=10, pady=5)
        material_cb = ttk.Combobox(top, values=[f"{m[1]} ({m[2]})" for m in self.all_materials], state="readonly")
        material_cb.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(top, text="Количество", font=FONT_SMALL).grid(row=1, column=0, padx=10, pady=5)
        quantity_entry = tk.Entry(top)
        quantity_entry.grid(row=1, column=1, padx=10, pady=5)

        def confirm():
            mat_idx = material_cb.current()
            if mat_idx == -1 or not quantity_entry.get().strip():
                messagebox.showwarning("Ошибка", "Выберите материал и укажите количество")
                return
            material_name = self.all_materials[mat_idx][1]
            unit = self.all_materials[mat_idx][2]
            try:
                quantity = float(quantity_entry.get())
            except ValueError:
                messagebox.showwarning("Ошибка", "Количество должно быть числом")
                return
            self.materials_tree.insert("", "end", values=(material_name, quantity, unit))
            top.destroy()

        tk.Button(top, text="Добавить", bg=ACCENT_COLOR, fg="black", command=confirm).grid(row=2, column=0, columnspan=2, pady=10)

    # --- Удаление материала из таблицы ---
    def remove_material(self):
        selected = self.materials_tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для удаления")
            return
        self.materials_tree.delete(selected)

    # --- Загрузка данных услуги и связанных материалов ---
    def load_service_data(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT code, name, type, description, min_cost, time_norm, estimated_cost, workshop_number, staff_count
            FROM services WHERE id=?
        """, (self.service_id,))
        service = cur.fetchone()
        if not service:
            messagebox.showerror("Ошибка", "Услуга не найдена")
            self.destroy()
            return
        for key, value in zip(self.fields.keys(), service):
            if value is not None:
                self.fields[key].delete(0, tk.END)
                self.fields[key].insert(0, value)

        # Загружаем материалы
        cur.execute("""
            SELECT m.name, sm.quantity_used, sm.unit
            FROM service_materials sm
            JOIN materials m ON sm.material_id = m.id
            WHERE sm.service_id=?
        """, (self.service_id,))
        for mat in cur.fetchall():
            self.materials_tree.insert("", "end", values=mat)
        conn.close()

    # --- Валидация данных ---
    def validate_fields(self):
        data = {key: self.fields[key].get().strip() for key in self.fields}
        for key in ["code", "name", "type", "min_cost"]:
            if not data[key]:
                messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно")
                return None
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

    # --- Сохранение услуги и связанных материалов ---
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
                self.service_id = cur.lastrowid

            # --- Сохраняем материалы ---
            cur.execute("DELETE FROM service_materials WHERE service_id=?", (self.service_id,))
            for item in self.materials_tree.get_children():
                mat_name, qty, unit = self.materials_tree.item(item)["values"]
                cur.execute("SELECT id FROM materials WHERE name=?", (mat_name,))
                mat_id = cur.fetchone()[0]
                cur.execute("INSERT INTO service_materials (service_id, material_id, quantity_used, unit) VALUES (?, ?, ?, ?)",
                            (self.service_id, mat_id, qty, unit))

            conn.commit()
            messagebox.showinfo("Успех", "Данные услуги сохранены")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
        finally:
            conn.close()
