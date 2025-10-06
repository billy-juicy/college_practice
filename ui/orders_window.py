import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.order_form import OrderFormWindow

class OrdersWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.withdraw()
        self.title("Заказы")
        self.geometry("1300x600")

        tk.Label(self, text="Список заказов", font=("Arial", 14, "bold")).pack(pady=10)

        columns = ("id", "partner_name", "manager_name", "created_at", "confirmed", "completed", "total_cost")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.edit_order_event)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_order).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_order).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_order).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.load_orders).pack(side="left", padx=5)
        tk.Button(button_frame, text="Назад", command=self.go_back).pack(side="right", padx=5)

        self.load_orders()

    def load_orders(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT o.id, p.name, e.full_name, o.created_at, 
                   o.confirmed, o.completed, o.total_cost
            FROM orders o
            JOIN partners p ON o.partner_id = p.id
            JOIN employees e ON o.manager_id = e.id
            ORDER BY o.created_at DESC
        """)
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def add_order(self):
        OrderFormWindow(self, on_save=self.load_orders)

    def edit_order_event(self, event):
        self.edit_order()

    def edit_order(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для редактирования")
            return
        order_id = self.tree.item(selected)["values"][0]
        OrderFormWindow(self, order_id=order_id, on_save=self.load_orders)

    def delete_order(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для удаления")
            return
        order_id = self.tree.item(selected)["values"][0]
        if not messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить заказ?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Заказ успешно удалён")
            self.load_orders()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить заказ: {e}")
        finally:
            conn.close()

    def go_back(self):
        self.master.deiconify()
        self.destroy()
