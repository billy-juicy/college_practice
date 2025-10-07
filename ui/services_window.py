import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.service_form import ServiceFormWindow
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL


class ServicesWindow(tk.Toplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.master.withdraw()
        self.user = user
        self.role = user[2]

        self.title("Услуги")
        self.geometry("1200x550")
        self.configure(bg=DEFAULT_BG)

        tk.Label(self, text="Список услуг", font=FONT_MAIN, bg=DEFAULT_BG).pack(pady=10)

        columns = ("id", "code", "name", "type", "description", "min_cost", "time_norm", "estimated_cost", "workshop_number", "staff_count")
        display = ("ID", "Код", "Наименование", "Тип", "Описание", "Мин. стоимость (₽)", "Норма времени (мин)", "Расчётная стоимость (₽)", "Цех", "Персонал")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, d in zip(columns, display):
            self.tree.heading(col, text=d)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.on_edit)

        style = ttk.Style()
        style.configure("Treeview", font=FONT_SMALL)
        style.configure("Treeview.Heading", font=FONT_MAIN)

        bf = tk.Frame(self, bg=DEFAULT_BG)
        bf.pack(pady=8)

        self.btn_add = tk.Button(bf, text="Добавить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL, width=12, command=self.add_service)
        self.btn_add.pack(side="left", padx=5)
        self.btn_edit = tk.Button(bf, text="Редактировать", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL, width=12, command=self.edit_service)
        self.btn_edit.pack(side="left", padx=5)
        self.btn_delete = tk.Button(bf, text="Удалить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL, width=12, command=self.delete_service)
        self.btn_delete.pack(side="left", padx=5)

        tk.Button(bf, text="Обновить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL, width=12, command=self.load_services).pack(side="left", padx=5)
        tk.Button(bf, text="Назад", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL, width=12, command=self.go_back).pack(side="right", padx=5)

        if self.role == "partner":
            self.btn_add.pack_forget()
            self.btn_edit.pack_forget()
            self.btn_delete.pack_forget()

        self.load_services()

    def load_services(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, code, name, type, description, min_cost, time_norm, estimated_cost, workshop_number, staff_count FROM services")
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)
        finally:
            conn.close()

    def get_selected_id(self):
        sel = self.tree.focus()
        if not sel:
            return None
        return self.tree.item(sel)["values"][0]

    def add_service(self):
        ServiceFormWindow(self, on_save=self.load_services)

    def edit_service(self):
        sid = self.get_selected_id()
        if not sid:
            messagebox.showwarning("Ошибка", "Выберите услугу")
            return
        ServiceFormWindow(self, service_id=sid, on_save=self.load_services)

    def on_edit(self, event):
        if self.role == "partner":
            # partner can view (open form in read mode — but current ServiceFormWindow always allows editing;
            # if you want strict read-only, adapt ServiceFormWindow to accept role/readonly flag)
            sid = self.get_selected_id()
            if sid:
                ServiceFormWindow(self, service_id=sid, on_save=None)
        else:
            self.edit_service()

    def delete_service(self):
        sid = self.get_selected_id()
        if not sid:
            messagebox.showwarning("Ошибка", "Выберите услугу")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить услугу?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM services WHERE id=?", (sid,))
            conn.commit()
            messagebox.showinfo("Успех", "Услуга удалена")
            self.load_services()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить услугу: {e}")
        finally:
            conn.close()

    def go_back(self):
        self.master.deiconify()
        self.destroy()
