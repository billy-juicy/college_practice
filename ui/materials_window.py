import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.material_form import MaterialFormWindow


class MaterialsWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Чистая планета — Материалы")
        self.master.geometry("1200x500")

        tk.Label(master, text="Список материалов", font=("Arial", 14, "bold")).pack(pady=10)

        # --- Таблица материалов ---
        columns = (
            "id", "type", "name", "quantity_per_package", "unit", "description",
            "image_url", "cost", "stock_quantity", "min_stock"
        )
        self.tree = ttk.Treeview(master, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.edit_material_event)

        # --- Панель кнопок ---
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_material).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_material).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_material).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.load_materials).pack(side="left", padx=5)
        tk.Button(button_frame, text="Назад", command=self.master.destroy).pack(side="right", padx=5)

        self.load_materials()

    # --- Загрузка данных ---
    def load_materials(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, type, name, quantity_per_package, unit, description,
                   image_url, cost, stock_quantity, min_stock
            FROM materials
        """)
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    # --- Добавление ---
    def add_material(self):
        MaterialFormWindow(self.master, on_save=self.load_materials)

    # --- Редактирование ---
    def edit_material_event(self, event):
        self.edit_material()

    def edit_material(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для редактирования")
            return
        material_id = self.tree.item(selected)["values"][0]
        MaterialFormWindow(self.master, material_id=material_id, on_save=self.load_materials)

    # --- Удаление ---
    def delete_material(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для удаления")
            return
        material_id = self.tree.item(selected)["values"][0]

        if not messagebox.askyesno("Подтверждение", "Удалить выбранный материал?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM materials WHERE id=?", (material_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Материал удалён")
            self.load_materials()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить материал: {e}")
        finally:
            conn.close()
