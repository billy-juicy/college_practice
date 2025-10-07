import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.material_form import MaterialFormWindow
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL


class MaterialsWindow(tk.Toplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.master.withdraw()
        self.user = user
        self.role = user[2]  # 'admin'|'manager'|'partner'

        self.title("Материалы")
        self.geometry("1000x550")
        self.configure(bg=DEFAULT_BG)

        tk.Label(self, text="Список материалов", font=FONT_MAIN, bg=DEFAULT_BG).pack(pady=10)

        columns = ("id", "name", "type", "quantity_per_package", "unit", "cost", "stock_quantity", "min_stock")
        display = ("ID", "Наименование", "Тип", "Кол-во в упаковке", "Ед. изм.", "Стоимость (₽)", "На складе", "Мин. запас")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col, d in zip(columns, display):
            self.tree.heading(col, text=d)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.on_edit)

        style = ttk.Style()
        style.configure("Treeview", font=FONT_SMALL)
        style.configure("Treeview.Heading", font=FONT_MAIN)

        # Buttons frame
        bf = tk.Frame(self, bg=DEFAULT_BG)
        bf.pack(pady=8)

        # keep references for role hiding
        self.btn_add = tk.Button(bf, text="Добавить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                                 width=12, command=self.add_material)
        self.btn_add.pack(side="left", padx=5)
        self.btn_edit = tk.Button(bf, text="Редактировать", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                                  width=12, command=self.edit_material)
        self.btn_edit.pack(side="left", padx=5)
        self.btn_delete = tk.Button(bf, text="Удалить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                                    width=12, command=self.delete_material)
        self.btn_delete.pack(side="left", padx=5)

        tk.Button(bf, text="Обновить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.load_materials).pack(side="left", padx=5)
        tk.Button(bf, text="Назад", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.go_back).pack(side="right", padx=5)

        # hide modification buttons for partners
        if self.role == "partner":
            self.btn_add.pack_forget()
            self.btn_edit.pack_forget()
            self.btn_delete.pack_forget()

        self.load_materials()

    def load_materials(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, name, type, quantity_per_package, unit, cost, stock_quantity, min_stock FROM materials")
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)
        finally:
            conn.close()

    def get_selected_id(self):
        sel = self.tree.focus()
        if not sel:
            return None
        return self.tree.item(sel)["values"][0]

    def add_material(self):
        MaterialFormWindow(self, on_save=self.load_materials)

    def edit_material(self):
        mid = self.get_selected_id()
        if not mid:
            messagebox.showwarning("Ошибка", "Выберите материал")
            return
        MaterialFormWindow(self, material_id=mid, on_save=self.load_materials)

    def on_edit(self, event):
        # double click handler
        if self.role == "partner":
            # partners can only view; optionally show details
            mid = self.get_selected_id()
            if mid:
                MaterialFormWindow(self, material_id=mid, on_save=None)  # open in edit window, but form allows view/edit — if you don't want partner to edit, you can modify MaterialFormWindow to respect role
        else:
            self.edit_material()

    def delete_material(self):
        mid = self.get_selected_id()
        if not mid:
            messagebox.showwarning("Ошибка", "Выберите материал")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить материал?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM materials WHERE id=?", (mid,))
            conn.commit()
            messagebox.showinfo("Успех", "Материал удалён")
            self.load_materials()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить материал: {e}")
        finally:
            conn.close()

    def go_back(self):
        self.master.deiconify()
        self.destroy()
