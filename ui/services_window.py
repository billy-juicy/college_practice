import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.service_form import ServiceFormWindow
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL

class ServicesWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.withdraw()
        self.title("Услуги")
        self.geometry("1100x500")
        self.configure(bg=DEFAULT_BG)

        tk.Label(self, text="Список услуг", font=FONT_MAIN, bg=DEFAULT_BG).pack(pady=10)

        columns = ("id", "code", "name", "type", "description", "min_cost", "time_norm", "estimated_cost")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Стиль Treeview
        style = ttk.Style()
        style.configure("Treeview", font=FONT_SMALL)
        style.configure("Treeview.Heading", font=FONT_MAIN)

        # Панель кнопок
        button_frame = tk.Frame(self, bg=DEFAULT_BG)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.add_service).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.edit_service).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.delete_service).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.load_services).pack(side="left", padx=5)
        tk.Button(button_frame, text="Назад", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL,
                  width=12, command=self.go_back).pack(side="right", padx=5)

        self.load_services()

    def load_services(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, code, name, type, description, min_cost, time_norm, estimated_cost FROM services")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def add_service(self):
        ServiceFormWindow(self, on_save=self.load_services)

    def edit_service(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу для редактирования")
            return
        service_id = self.tree.item(selected)["values"][0]
        ServiceFormWindow(self, service_id=service_id, on_save=self.load_services)

    def delete_service(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите услугу для удаления")
            return
        service_id = self.tree.item(selected)["values"][0]
        if not messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить услугу?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM services WHERE id=?", (service_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Услуга успешно удалена")
            self.load_services()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить услугу: {e}")
        finally:
            conn.close()

    def go_back(self):
        self.master.deiconify()
        self.destroy()
