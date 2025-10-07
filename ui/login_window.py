import os
import tkinter as tk
from tkinter import messagebox
import hashlib
from logic.db_utils import get_connection
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL
from PIL import Image, ImageTk


class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Чистая планета — Вход")
        self.master.geometry("400x300")
        self.master.configure(bg=DEFAULT_BG)

        try:
            icon_path = os.path.join("resources", "icon.png")
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_image.thumbnail((64, 64), resample=Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(icon_image)
                self.master.iconphoto(True, self.icon_photo)
            else:
                print(f"Иконка не найдена по пути: {icon_path}")
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")

        # --- Email ---
        tk.Label(master, text="Email:", bg=DEFAULT_BG, font=FONT_MAIN).pack(pady=5)
        self.email_entry = tk.Entry(master, width=30, font=FONT_SMALL)
        self.email_entry.pack(pady=5)

        # --- Пароль ---
        tk.Label(master, text="Пароль:", bg=DEFAULT_BG, font=FONT_MAIN).pack(pady=5)
        self.password_entry = tk.Entry(master, show="*", width=30, font=FONT_SMALL)
        self.password_entry.pack(pady=5)

        # --- Панель кнопок ---
        button_frame = tk.Frame(master, bg=DEFAULT_BG)
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="Войти", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.login).pack(side="left", padx=5)
        tk.Button(button_frame, text="Регистрация", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.open_register).pack(side="left", padx=5)

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Ошибка", "Введите email и пароль")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, full_name, role, password FROM employees WHERE email=?", (email,))
            user = cur.fetchone()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обращении к базе: {e}")
            return
        finally:
            conn.close()

        if not user:
            messagebox.showerror("Ошибка", "Пользователь не найден")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()
        if user[3] != hashed:
            messagebox.showerror("Ошибка", "Неверный пароль")
            return

        # Успешный вход — переход на MainWindow
        self.master.destroy()
        import ui.main_window as main_module
        root = tk.Tk()
        main_module.MainWindow(root, user)
        root.mainloop()

    def open_register(self):
        # Переход на окно регистрации
        self.master.destroy()
        import ui.register_window as reg_module
        root = tk.Tk()
        reg_module.RegisterWindow(root)
        root.mainloop()
