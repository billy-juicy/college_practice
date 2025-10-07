import tkinter as tk
from tkinter import ttk, messagebox
from logic.db_utils import get_connection
from datetime import datetime
from resources.constants import DEFAULT_BG, ACCENT_COLOR, FONT_MAIN, FONT_SMALL


class OrderFormWindow(tk.Toplevel):
    def __init__(self, master, order_id=None, on_save=None):
        super().__init__(master)
        self.order_id = order_id
        self.on_save = on_save
        self.title("Добавить заказ" if order_id is None else "Редактировать заказ")
        self.geometry("600x550")
        self.resizable(False, False)
        self.configure(bg=DEFAULT_BG)

        # --- Инициализация переменных ---
        self.partner_var = tk.StringVar()
        self.manager_var = tk.StringVar()
        self.service_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.total_cost_var = tk.StringVar(value="0.00")
        self.completed_var = tk.IntVar(value=0)

        # --- Поля формы ---
        labels = [
            ("Партнёр", self.partner_var),
            ("Менеджер", self.manager_var),
            ("Услуга", self.service_var),
            ("Количество", self.quantity_var),
            ("Общая стоимость (₽)", self.total_cost_var)
        ]

        for i, (text, var) in enumerate(labels):
            tk.Label(self, text=text, font=FONT_MAIN, bg=DEFAULT_BG).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if text in ["Партнёр", "Менеджер", "Услуга"]:
                entry = ttk.Combobox(self, textvariable=var, state="readonly", font=FONT_SMALL)
            elif text == "Общая стоимость (₽)":
                entry = tk.Label(self, textvariable=var, font=FONT_SMALL, bg=DEFAULT_BG)
            else:
                entry = tk.Entry(self, textvariable=var, font=FONT_SMALL)
            entry.grid(row=i, column=1, padx=10, pady=5)

        # --- Чекбокс "Выполнен" ---
        tk.Checkbutton(self, text="Заказ выполнен", variable=self.completed_var,
                       bg=DEFAULT_BG, font=FONT_MAIN).grid(row=5, column=0, columnspan=2, pady=5)

        # --- Кнопки ---
        button_frame = tk.Frame(self, bg=DEFAULT_BG)
        button_frame.grid(row=7, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Рассчитать", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.calculate_total_cost).pack(side="left", padx=5)
        tk.Button(button_frame, text="Сохранить", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.save_order).pack(side="left", padx=5)
        tk.Button(button_frame, text="Отмена", bg=ACCENT_COLOR, fg="black",
                  font=FONT_SMALL, width=12, command=self.destroy).pack(side="left", padx=5)

        # --- Загрузка данных в списки ---
        self.load_comboboxes()

        # --- Загрузка данных заказа при редактировании ---
        if self.order_id:
            self.load_order_data()

    def load_comboboxes(self):
        conn = get_connection()
        cur = conn.cursor()

        # Партнёры
        cur.execute("SELECT id, name FROM partners")
        partners = cur.fetchall()
        self.partners_map = {f"{name} (ID {pid})": pid for pid, name in partners}
        self.partner_cb = self.nametowidget(self.grid_slaves(row=0, column=1)[0])
        self.partner_cb["values"] = list(self.partners_map.keys())

        # Менеджеры
        cur.execute("SELECT id, full_name FROM employees WHERE role='manager'")
        managers = cur.fetchall()
        self.managers_map = {f"{name} (ID {mid})": mid for mid, name in managers}
        self.manager_cb = self.nametowidget(self.grid_slaves(row=1, column=1)[0])
        self.manager_cb["values"] = list(self.managers_map.keys())

        # Услуги
        cur.execute("SELECT id, name, COALESCE(estimated_cost, min_cost, 0) FROM services")
        services = cur.fetchall()
        # два словаря для корректного редактирования
        self.services_map = {f"{name} (₽{cost:.2f})": (sid, cost) for sid, name, cost in services}
        self.services_by_id = {sid: f"{name} (₽{cost:.2f})" for sid, name, cost in services}
        self.service_cb = self.nametowidget(self.grid_slaves(row=2, column=1)[0])
        self.service_cb["values"] = list(self.services_map.keys())

        conn.close()

    def calculate_total_cost(self):
        try:
            quantity = int(self.quantity_var.get())
            _, cost_per_unit = self.services_map[self.service_var.get()]
            total = quantity * cost_per_unit
            self.total_cost_var.set(f"{total:.2f}")
        except Exception:
            messagebox.showwarning("Ошибка", "Выберите услугу и укажите корректное количество")

    def load_order_data(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT partner_id, manager_id, total_cost, completed, final_payment_date FROM orders WHERE id=?", (self.order_id,))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Ошибка", "Заказ не найден")
            self.destroy()
            conn.close()
            return

        partner_id, manager_id, total, completed, final_date = row

        # Партнёр и менеджер
        for key, value in self.partners_map.items():
            if value == partner_id:
                self.partner_var.set(key)
                break
        for key, value in self.managers_map.items():
            if value == manager_id:
                self.manager_var.set(key)
                break

        self.total_cost_var.set(f"{total:.2f}" if total else "0.00")
        self.completed_var.set(completed)

        # Услуга и количество
        cur.execute("""
            SELECT service_id, quantity
            FROM order_services
            WHERE order_id=?
        """, (self.order_id,))
        service_row = cur.fetchone()
        conn.close()

        if service_row:
            sid, quantity = service_row
            if sid in self.services_by_id:
                self.service_var.set(self.services_by_id[sid])
                self.quantity_var.set(str(quantity))

    def check_stock(self, service_id, quantity):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.name, m.stock_quantity, sm.quantity_used
            FROM service_materials sm
            JOIN materials m ON sm.material_id = m.id
            WHERE sm.service_id=?
        """, (service_id,))
        for name, stock, qty_used in cur.fetchall():
            if stock < qty_used * quantity:
                conn.close()
                return False, name
        conn.close()
        return True, ""

    def consume_materials(self, service_id, quantity):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT material_id, quantity_used FROM service_materials WHERE service_id=?", (service_id,))
            for mat_id, qty_used in cur.fetchall():
                total_used = qty_used * quantity
                cur.execute("UPDATE materials SET stock_quantity = stock_quantity - ? WHERE id=?", (total_used, mat_id))
            conn.commit()
        finally:
            conn.close()

    def return_materials(self, service_id, quantity):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT material_id, quantity_used FROM service_materials WHERE service_id=?", (service_id,))
            for mat_id, qty_used in cur.fetchall():
                total_return = qty_used * quantity
                cur.execute("UPDATE materials SET stock_quantity = stock_quantity + ? WHERE id=?", (total_return, mat_id))
            conn.commit()
        finally:
            conn.close()

    def save_order(self):
        if not self.partner_var.get() or not self.manager_var.get() or not self.service_var.get():
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return

        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Количество должно быть положительным числом")
            return

        partner_id = self.partners_map[self.partner_var.get()]
        manager_id = self.managers_map[self.manager_var.get()]
        service_id, cost_per_unit = self.services_map[self.service_var.get()]
        total_cost = quantity * cost_per_unit
        completed = self.completed_var.get()
        completed_date = datetime.now().strftime("%Y-%m-%d") if completed else None

        ok, mat_name = self.check_stock(service_id, quantity)
        if not ok:
            messagebox.showerror("Ошибка", f"Недостаточно материала: {mat_name}")
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            if self.order_id:
                cur.execute("SELECT service_id, quantity FROM order_services WHERE order_id=?", (self.order_id,))
                old_service = cur.fetchone()
                if old_service:
                    old_sid, old_qty = old_service
                    self.return_materials(old_sid, old_qty)

                cur.execute("""
                    UPDATE orders
                    SET partner_id=?, manager_id=?, total_cost=?, confirmed=1, completed=?, final_payment_date=?
                    WHERE id=?
                """, (partner_id, manager_id, total_cost, completed, completed_date, self.order_id))
                order_id = self.order_id
                cur.execute("DELETE FROM order_services WHERE order_id=?", (order_id,))
            else:
                cur.execute("""
                    INSERT INTO orders (partner_id, manager_id, total_cost, confirmed, completed, created_at, final_payment_date)
                    VALUES (?, ?, ?, 1, ?, ?, ?)
                """, (partner_id, manager_id, total_cost, completed, datetime.now(), completed_date))
                order_id = cur.lastrowid

            cur.execute("""
                INSERT INTO order_services (order_id, service_id, quantity, cost_per_unit, total_cost, expected_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_id, service_id, quantity, cost_per_unit, total_cost, completed_date))
            conn.commit()

            self.consume_materials(service_id, quantity)

            messagebox.showinfo("Успех", "Заказ сохранён")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить заказ: {e}")
        finally:
            conn.close()