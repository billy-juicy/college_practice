import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from logic.data_fetcher import get_partners
from ui.partner_form import PartnerFormWindow
from ui.service_history import ServiceHistoryWindow
from ui.materials_window import MaterialsWindow
from ui.services_window import ServicesWindow
from ui.orders_window import OrdersWindow
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL

class MainWindow:
    def __init__(self, master, user):
        self.master = master
        self.user = user
        self.master.title("Чистая планета — Партнёры")
        self.master.geometry("1200x700")
        self.master.configure(bg=DEFAULT_BG)

        # Иконка приложения
        try:
            icon_path = os.path.join("resources", "icon.png")
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_image.thumbnail((64, 64), resample=Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon_image)
                self.master.iconphoto(True, self.icon_photo)
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")

        # Логотип
        try:
            logo_path = os.path.join("resources", "icon.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                max_width = 300
                ratio = max_width / logo_image.width
                new_size = (int(logo_image.width * ratio), int(logo_image.height * ratio))
                logo_image = logo_image.resize(new_size, resample=Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                tk.Label(master, image=self.logo_photo, bg=DEFAULT_BG).pack(pady=10)
        except Exception as e:
            print(f"Не удалось загрузить логотип: {e}")

        # Приветствие
        tk.Label(master, text=f"Добро пожаловать, {user[1]} ({user[2]})",
                 bg=DEFAULT_BG, font=FONT_MAIN).pack(pady=5)

        # Панель кнопок
        button_frame = tk.Frame(master, bg=DEFAULT_BG)
        button_frame.pack(pady=5)

        self.add_partner_btn = tk.Button(button_frame, text="Добавить партнёра", bg=ACCENT_COLOR, fg="black",
                                         font=FONT_SMALL, command=self.add_partner)
        self.add_partner_btn.pack(side="left", padx=5)

        self.edit_selected_partner_btn = tk.Button(button_frame, text="Редактировать", bg=ACCENT_COLOR, fg="black",
                                                   font=FONT_SMALL, command=self.edit_selected_partner)
        self.edit_selected_partner_btn.pack(side="left", padx=5)

        tk.Button(button_frame, text="История услуг", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.open_history_selected).pack(side="left", padx=5)

        tk.Button(button_frame, text="Удалить", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.delete_selected_partner).pack(side="left", padx=5)

        tk.Button(button_frame, text="Обновить", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.load_partners).pack(side="left", padx=5)

        self.open_materials_btn = tk.Button(button_frame, text="Материалы", bg=ACCENT_COLOR, fg="black",
                                            font=FONT_SMALL, command=self.open_materials)
        self.open_materials_btn.pack(side="left", padx=5)

        self.open_services_btn = tk.Button(button_frame, text="Услуги", bg=ACCENT_COLOR, fg="black",
                                           font=FONT_SMALL, command=self.open_services)
        self.open_services_btn.pack(side="left", padx=5)

        self.open_orders_btn = tk.Button(button_frame, text="Заказы", bg=ACCENT_COLOR, fg="black",
                                         font=FONT_SMALL, command=self.open_orders)
        self.open_orders_btn.pack(side="left", padx=5)

        tk.Button(button_frame, text="Выход", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, command=self.master.destroy).pack(side="right", padx=5)

        # Область скролла для карточек
        self.canvas = tk.Canvas(master, bg=DEFAULT_BG)
        self.scrollbar = tk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=DEFAULT_BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.selected_card = None
        self.load_partners()

        # Скрываем кнопки для партнёров
        if self.user[2] == "partner":
            self.add_partner_btn.pack_forget()
            self.edit_selected_partner_btn.pack_forget()
            self.open_materials_btn.pack_forget()
            self.open_services_btn.pack_forget()
            self.open_orders_btn.pack_forget()

    # --- Загрузка партнёров ---
    def load_partners(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        partners = get_partners()
        # если пользователь — партнёр, показываем только свои карточки
        if self.user[2] == "partner" and self.user[3]:
            partners = [p for p in partners if p[0] == self.user[3]]

        for partner in partners:
            self.add_partner_card(partner)

    # --- Создание карточки партнёра ---
    def add_partner_card(self, partner):
        card = tk.Frame(self.scrollable_frame, bg="white", bd=1, relief="solid", padx=10, pady=5)
        card.pack(fill="x", pady=5, padx=10)
        card.partner_id = partner[0]
        card.selected = False

        def on_click(event, c=card):
            if self.selected_card:
                self.selected_card.config(bg="white")
                self.selected_card.selected = False
            c.config(bg="#d0f0d0")
            c.selected = True
            self.selected_card = c

        card.bind("<Button-1>", on_click)

        fields = ["ID", "Наименование", "Тип", "Рейтинг", "Юридический адрес", "ИНН",
                  "ФИО руководителя", "Телефон", "Email", "Логотип"]
        for i, value in enumerate(partner):
            lbl = tk.Label(card, text=f"{fields[i]}: {value}", font=FONT_SMALL, bg="white", anchor="w")
            lbl.pack(fill="x")
            lbl.bind("<Button-1>", on_click)

    # --- Кнопки сверху ---
    def add_partner(self):
        PartnerFormWindow(self.master, on_save=self.load_partners)

    def edit_selected_partner(self):
        if not self.selected_card:
            messagebox.showwarning("Ошибка", "Выберите партнёра")
            return
        PartnerFormWindow(self.master, partner_id=self.selected_card.partner_id, on_save=self.load_partners)

    def open_history_selected(self):
        if not self.selected_card:
            messagebox.showwarning("Ошибка", "Выберите партнёра")
            return
        ServiceHistoryWindow(self.master, self.selected_card.partner_id)

    def delete_selected_partner(self):
        if not self.selected_card:
            messagebox.showwarning("Ошибка", "Выберите партнёра")
            return
        if not messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить партнёра?"):
            return
        from logic.db_utils import get_connection
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM partners WHERE id=?", (self.selected_card.partner_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Партнёр успешно удалён")
            self.load_partners()
        finally:
            conn.close()

    # --- Переходы на другие окна ---
    def open_materials(self):
        MaterialsWindow(self.master, self.user)

    def open_services(self):
        ServicesWindow(self.master, self.user)

    def open_orders(self):
        OrdersWindow(self.master, self.user)
