import tkinter as tk
from tkinter import ttk
from logic.data_fetcher import get_partner_service_history
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

        # Настройка колонок
        self.tree.column("name", width=250, anchor="center")
        self.tree.column("quantity", width=100, anchor="center")
        self.tree.column("date", width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        # Кнопка Закрыть
        tk.Button(self, text="Закрыть", bg=ACCENT_COLOR, fg="black", font=FONT_SMALL, width=12,
                  command=self.destroy).pack(pady=10)

        self.load_data(partner_id)

    def load_data(self, partner_id):
        self.tree.delete(*self.tree.get_children())
        data = get_partner_service_history(partner_id)
        for d in data:
            self.tree.insert("", "end", values=d)
