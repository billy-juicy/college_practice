import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.service_form import ServiceFormWindow


class ServicesWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Чистая планета — Услуги")
        self.master.geometry("1200x500")

        tk.Label(master, text="Список услуг", font=("Arial", 14, "bold")).pack(pady=10)

        # --- Таблица услуг ---
        columns = ("id", "code", "name", "type", "description", "min_cost",
                   "time_norm", "estimated_cost", "workshop_number", "staff_count")
        self.tree = ttk.Treeview(master, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.edit_service_event)

        # --- Панель кнопок ---
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_service).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_service).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_service).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.load_services).pack(side="left", padx=5)
        tk.Button(button_frame, text="Назад", command=self.master.destroy).pack(side="right", padx=5)

        self.load_services()

    # --- Загрузка данных ---
    def load_services(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, code, name, type, description, min_cost,
                   time_norm, estimated_cost, workshop_number, staff_count
            FROM services
        """)
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    # --- Добавление ---
    def add_service(self):
        ServiceFormWindow(self.master, on_save=self.load_services)

    # --- Редактирование ---
    def edit_service_event(self, event):
        self.edit_service()

    def edit_service(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу для редактирования")
            return
        service_id = self.tree.item(selected)["values"][0]
        ServiceFormWindow(self.master, service_id=service_id, on_save=self.load_services)

    # --- Удаление ---
    def delete_service(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу для удаления")
            return
        service_id = self.tree.item(selected)["values"][0]

        if not messagebox.askyesno("Подтверждение", "Удалить выбранную услугу?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM services WHERE id=?", (service_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Услуга удалена")
            self.load_services()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить услугу: {e}")
        finally:
            conn.close()
