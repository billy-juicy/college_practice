import tkinter as tk
from tkinter import ttk
from logic.data_fetcher import get_partner_service_history

class ServiceHistoryWindow(tk.Toplevel):
    def __init__(self, master, partner_id):
        super().__init__(master)
        self.title("История услуг партнёра")
        self.geometry("600x400")

        self.tree = ttk.Treeview(self, columns=("name", "quantity", "date"), show="headings")
        self.tree.heading("name", text="Наименование услуги")
        self.tree.heading("quantity", text="Количество")
        self.tree.heading("date", text="Дата выполнения")
        self.tree.pack(fill="both", expand=True, pady=10)

        tk.Button(self, text="Закрыть", command=self.destroy).pack(pady=10)
        self.load_data(partner_id)

    def load_data(self, partner_id):
        data = get_partner_service_history(partner_id)
        for d in data:
            self.tree.insert("", "end", values=d)
