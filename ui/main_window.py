import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from logic.data_fetcher import get_partners
from ui.partner_form import PartnerFormWindow
from ui.service_history import ServiceHistoryWindow

# Импорт окон для материалов, услуг и заказов
from ui.materials_window import MaterialsWindow
from ui.services_window import ServicesWindow
from ui.orders_window import OrdersWindow

from resources.constants import DEFAULT_BG, ALT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL

class MainWindow:
    def __init__(self, master, user):
        self.master = master
        self.user = user
        self.master.title("Чистая планета — Партнёры")
        self.master.geometry("1920x600")
        self.master.configure(bg=DEFAULT_BG)

        # --- Иконка приложения ---
        try:
            self.master.iconphoto(True, tk.PhotoImage(file="resources/icon.png"))
        except Exception:
            print("Не удалось загрузить иконку")

        # --- Логотип ---
        try:
            logo_image = Image.open("resources/logo.png")
            logo_photo = ImageTk.PhotoImage(logo_image)
            tk.Label(master, image=logo_photo, bg=DEFAULT_BG).pack(pady=10)
            self.logo_photo = logo_photo  # чтобы изображение не удалилось сборщиком мусора
        except Exception:
            print("Не удалось загрузить логотип")

        # --- Приветствие ---
        tk.Label(master, text=f"Добро пожаловать, {user[1]} ({user[2]})",
                 bg=DEFAULT_BG, font=FONT_MAIN).pack(pady=5)

        # --- Treeview с партнёрами ---
        columns = ("id", "name", "type", "rating", "legal_address", "inn",
                   "director_name", "phone", "email", "logo_url")
        self.tree = ttk.Treeview(master, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.edit_partner_event)

        style = ttk.Style()
        style.configure("Treeview", font=FONT_SMALL)
        style.configure("Treeview.Heading", font=FONT_MAIN)

        # --- Панель кнопок ---
        button_frame = tk.Frame(master, bg=DEFAULT_BG)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Добавить партнёра", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.add_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="Редактировать", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.edit_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.delete_partner).pack(side="left", padx=5)
        tk.Button(button_frame, text="История услуг", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.open_history).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.load_partners).pack(side="left", padx=5)
        tk.Button(button_frame, text="Материалы", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.open_materials).pack(side="left", padx=5)
        tk.Button(button_frame, text="Услуги", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.open_services).pack(side="left", padx=5)
        tk.Button(button_frame, text="Заказы", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.open_orders).pack(side="left", padx=5)
        tk.Button(button_frame, text="Выход", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.master.destroy).pack(side="right", padx=5)

        # Загрузка данных партнёров
        self.load_partners()

    # --- Работа с партнёрами ---
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

    # --- Переход на другие окна ---
    def open_materials(self):
        MaterialsWindow(self.master)

    def open_services(self):
        ServicesWindow(self.master)

    def open_orders(self):
        OrdersWindow(self.master)
