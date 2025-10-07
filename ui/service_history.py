import tkinter as tk
from tkinter import ttk
from logic.db_utils import get_connection
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL

class ServiceHistoryWindow(tk.Toplevel):
    def __init__(self, master, partner_id):
        super().__init__(master)
        self.title("История услуг партнёра")
        self.geometry("600x400")
        self.configure(bg=DEFAULT_BG)

        tk.Label(self, text="История услуг партнёра", font=FONT_MAIN, bg=DEFAULT_BG).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("name", "quantity", "date"), show="headings")
        self.tree.heading("name", text="Наименование услуги")
        self.tree.heading("quantity", text="Количество")
        self.tree.heading("date", text="Дата выполнения")

        self.tree.column("name", width=250, anchor="center")
        self.tree.column("quantity", width=100, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=10)

        tk.Button(self, text="Закрыть", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL, width=12,
                  command=self.destroy).pack(pady=10)

        self.load_data(partner_id)

    def load_data(self, partner_id):
        self.tree.delete(*self.tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.name, os.quantity, o.final_payment_date
            FROM orders o
            JOIN order_services os ON o.id = os.order_id
            JOIN services s ON os.service_id = s.id
            WHERE o.partner_id = ? AND o.completed = 1
            ORDER BY o.final_payment_date DESC
        """, (partner_id,))
        for name, quantity, date in cur.fetchall():
            self.tree.insert("", "end", values=(name, quantity, date))
        conn.close()