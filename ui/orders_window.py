import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from ui.order_form import OrderFormWindow


class OrdersWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Чистая планета — Заказы")
        self.master.geometry("1300x600")

        tk.Label(master, text="Список заказов", font=("Arial", 14, "bold")).pack(pady=10)

        # Таблица заказов
        columns = (
            "id", "partner_name", "manager_name", "created_at",
            "confirmed", "completed", "total_cost"
        )
        self.tree = ttk.Treeview(master, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.edit_order_event)

        # Панель кнопок
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Добавить заказ", command=self.add_order).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_order).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_order).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.load_orders).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Назад", command=self.master.destroy).pack(side="right", padx=5)

        self.load_orders()

    def load_orders(self):
        """Загрузка заказов с именами партнёров и менеджеров"""
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
        OrderFormWindow(self.master, on_save=self.load_orders)

    def edit_order_event(self, event):
        self.edit_order()

    def edit_order(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для редактирования")
            return
        order_id = self.tree.item(selected)["values"][0]
        OrderFormWindow(self.master, order_id=order_id, on_save=self.load_orders)

    def delete_order(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ для удаления")
            return
        order_id = self.tree.item(selected)["values"][0]

        if not messagebox.askyesno("Подтверждение", "Удалить выбранный заказ?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Заказ удалён")
            self.load_orders()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить заказ: {e}")
        finally:
            conn.close()
