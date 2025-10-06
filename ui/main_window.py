import tkinter as tk
from tkinter import ttk, messagebox
from logic.data_fetcher import get_partners
from logic.db_utils import get_connection
from ui.service_history import ServiceHistoryWindow
from ui.partner_form import PartnerFormWindow  # форма для добавления/редактирования партнёра

class MainWindow:
    def __init__(self, master, user):
        self.master = master
        self.user = user
        self.master.title("Чистая планета — Партнёры")
        self.master.geometry("1920x500")

        tk.Label(master, text=f"Добро пожаловать, {user[1]} ({user[2]})").pack(pady=10)

        # Treeview с партнёрами, теперь со всеми полями
        self.tree = ttk.Treeview(master, columns=("id", "name", "type", "rating",
                                                  "legal_address", "inn", "director_name",
                                                  "phone", "email", "logo_url"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Наименование")
        self.tree.heading("type", text="Тип")
        self.tree.heading("rating", text="Рейтинг")
        self.tree.heading("legal_address", text="Адрес")
        self.tree.heading("inn", text="ИНН")
        self.tree.heading("director_name", text="Руководитель")
        self.tree.heading("phone", text="Телефон")
        self.tree.heading("email", text="Email")
        self.tree.heading("logo_url", text="Логотип")
        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.edit_partner_event)  # двойной клик для редактирования

        # Кнопки управления
        button_frame = tk.Frame(master)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Добавить партнёра", command=self.add_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="История услуг", command=self.open_history).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.load_partners).pack(side="left", padx=5)
        tk.Button(button_frame, text="Выход", command=self.master.destroy).pack(side="right", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_partner).pack(side="left", padx=5)

        self.load_partners()

    def load_partners(self):
        self.tree.delete(*self.tree.get_children())
        for p in get_partners():
            # Здесь предполагается, что get_partners возвращает все необходимые поля
            self.tree.insert("", "end", values=p)

    def open_history(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите партнёра")
            return
        partner_id = self.tree.item(selected)["values"][0]
        ServiceHistoryWindow(self.master, partner_id)

    # --- Добавление партнёра ---
    def add_partner(self):
        PartnerFormWindow(self.master, on_save=self.load_partners)

    # --- Редактирование партнёра ---
    def edit_partner_event(self, event):
        self.edit_partner()

    def edit_partner(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите партнёра для редактирования")
            return
        partner_id = self.tree.item(selected)["values"][0]
        PartnerFormWindow(self.master, partner_id=partner_id, on_save=self.load_partners)

    def delete_partner(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите партнёра для удаления")
            return

        partner_id = self.tree.item(selected)["values"][0]

        if not messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить партнёра?"):
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM partners WHERE id=?", (partner_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Партнёр успешно удалён")
            self.load_partners()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить партнёра: {e}")
        finally:
            conn.close()
