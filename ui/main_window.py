import tkinter as tk
from tkinter import ttk, messagebox
from logic.data_fetcher import get_partners
from ui.partner_form import PartnerFormWindow
from ui.service_history import ServiceHistoryWindow
from ui.materials_window import MaterialsWindow
from ui.services_window import ServicesWindow
from ui.orders_window import OrdersWindow


class MainWindow:
    def __init__(self, master, user):
        self.master = master
        self.user = user
        self.master.title("Чистая планета — Партнёры")
        self.master.geometry("1920x500")

        tk.Label(master, text=f"Добро пожаловать, {user[1]} ({user[2]})").pack(pady=10)

        # Treeview с партнёрами
        self.tree = ttk.Treeview(master, columns=(
            "id", "name", "type", "rating", "legal_address", "inn",
            "director_name", "phone", "email", "logo_url"
        ), show="headings")
        headings = {
            "id": "ID",
            "name": "Наименование",
            "type": "Тип",
            "rating": "Рейтинг",
            "legal_address": "Адрес",
            "inn": "ИНН",
            "director_name": "Руководитель",
            "phone": "Телефон",
            "email": "Email",
            "logo_url": "Логотип"
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.edit_partner_event)

        # Кнопки управления
        button_frame = tk.Frame(master)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Добавить партнёра", command=self.add_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="История услуг", command=self.open_history).pack(side="left", padx=5)
        tk.Button(button_frame, text="Материалы", command=self.open_materials).pack(side="left", padx=5)
        tk.Button(button_frame, text="Услуги", command=self.open_services).pack(side="left", padx=5)
        tk.Button(button_frame, text="Заказы", command=self.open_orders).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.load_partners).pack(side="left", padx=5)
        tk.Button(button_frame, text="Выход", command=self.master.destroy).pack(side="right", padx=5)

        self.load_partners()

    def load_partners(self):
        self.tree.delete(*self.tree.get_children())
        for p in get_partners():
            self.tree.insert("", "end", values=p)

    def add_partner(self):
        PartnerFormWindow(self.master, on_save=self.load_partners)

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
        from logic.db_utils import get_connection
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

    def open_history(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите партнёра")
            return
        partner_id = self.tree.item(selected)["values"][0]
        ServiceHistoryWindow(self.master, partner_id)

    # --- Открытие других окон ---
    def open_materials(self):
        MaterialsWindow(self.master)

    def open_services(self):
        ServicesWindow(self.master)

    def open_orders(self):
        OrdersWindow(self.master)
