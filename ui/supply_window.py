import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.supply_form import SupplyFormWindow


class SupplyWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Чистая планета — Поставки материалов")
        self.master.geometry("1300x550")

        tk.Label(master, text="Поставки материалов", font=("Arial", 14, "bold")).pack(pady=10)

        # --- Таблица ---
        columns = ("id", "material_id", "supplier_name", "quantity", "cost_per_unit",
                   "total_cost", "supply_date", "employee_name")
        self.tree = ttk.Treeview(master, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.edit_supply_event)

        # --- Кнопки ---
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_supply).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_supply).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_supply).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.load_supplies).pack(side="left", padx=5)
        tk.Button(button_frame, text="Назад", command=self.master.destroy).pack(side="right", padx=5)

        self.load_supplies()

    def load_supplies(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT sm.id, sm.material_id, m.name AS material_name, sm.quantity, sm.cost_per_unit,
                   (sm.quantity * sm.cost_per_unit) AS total_cost, sm.supply_date, e.full_name AS employee_name
            FROM supplier_materials sm
            LEFT JOIN materials m ON sm.material_id = m.id
            LEFT JOIN employees e ON sm.employee_id = e.id
            ORDER BY sm.supply_date DESC
        """)
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def add_supply(self):
        SupplyFormWindow(self.master, on_save=self.load_supplies)

    def edit_supply_event(self, event):
        self.edit_supply()

    def edit_supply(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите поставку для редактирования")
            return
        supply_id = self.tree.item(selected)["values"][0]
        SupplyFormWindow(self.master, supply_id=supply_id, on_save=self.load_supplies)

    def delete_supply(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите поставку для удаления")
            return
        supply_id = self.tree.item(selected)["values"][0]

        if not messagebox.askyesno("Подтверждение", "Удалить выбранную поставку?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM supplier_materials WHERE id=?", (supply_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Поставка удалена")
            self.load_supplies()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить поставку: {e}")
        finally:
            conn.close()
