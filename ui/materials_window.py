import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.material_form import MaterialFormWindow

class MaterialsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.withdraw()  # Скрываем главную форму
        self.title("Материалы")
        self.geometry("900x500")

        tk.Label(self, text="Список материалов", font=("Arial", 14, "bold")).pack(pady=10)

        # Таблица
        columns = ("id", "name", "type", "quantity_per_package", "unit", "cost", "stock_quantity")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Панель кнопок
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_material).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_material).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_material).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.load_materials).pack(side="left", padx=5)
        tk.Button(button_frame, text="Назад", command=self.go_back).pack(side="right", padx=5)

        self.load_materials()

    def load_materials(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, type, quantity_per_package, unit, cost, stock_quantity FROM materials")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def add_material(self):
        MaterialFormWindow(self, on_save=self.load_materials)

    def edit_material(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для редактирования")
            return
        material_id = self.tree.item(selected)["values"][0]
        MaterialFormWindow(self, material_id=material_id, on_save=self.load_materials)

    def delete_material(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для удаления")
            return
        material_id = self.tree.item(selected)["values"][0]
        if not messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить материал?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM materials WHERE id=?", (material_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Материал успешно удалён")
            self.load_materials()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить материал: {e}")
        finally:
            conn.close()

    def go_back(self):
        self.master.deiconify()
        self.destroy()
