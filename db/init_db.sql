-- Таблица сотрудников
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    birth_date DATE,
    passport TEXT,
    bank_account TEXT,
    position TEXT,
    health_status TEXT,
    phone TEXT,
    email TEXT,
    role TEXT,
    password TEXT
);

-- Таблица партнеров
CREATE TABLE partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    name TEXT NOT NULL,
    legal_address TEXT,
    inn TEXT,
    director_name TEXT,
    phone TEXT,
    email TEXT,
    logo_url TEXT,
    rating REAL DEFAULT 0.00
);

-- Таблица заказов
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_id INTEGER NOT NULL,
    manager_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    prepayment_made INTEGER DEFAULT 0,
    prepayment_date DATE,
    confirmed INTEGER DEFAULT 0,
    completed INTEGER DEFAULT 0,
    total_cost REAL,
    final_payment_date DATE,
    FOREIGN KEY (partner_id) REFERENCES partners(id),
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- Таблица услуг
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    type TEXT,
    name TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    min_cost REAL,
    time_norm INTEGER,
    estimated_cost REAL,
    workshop_number INTEGER,
    staff_count INTEGER
);

-- Таблица связи заказов и услуг
CREATE TABLE order_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    cost_per_unit REAL,
    total_cost REAL,
    expected_date DATE,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

-- Таблица материалов
CREATE TABLE materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    name TEXT NOT NULL,
    quantity_per_package INTEGER,
    unit TEXT,
    description TEXT,
    image_url TEXT,
    cost REAL,
    stock_quantity INTEGER,
    min_stock INTEGER
);

-- Таблица поставщиков
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    inn TEXT
);

-- Таблица поставок материалов
CREATE TABLE supplier_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    supply_date DATE,
    quantity INTEGER,
    price REAL,
    employee_id INTEGER NOT NULL,
    FOREIGN KEY (material_id) REFERENCES materials(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Таблица связи услуг и материалов
CREATE TABLE service_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    quantity_used REAL,
    unit TEXT,
    UNIQUE (service_id, material_id),
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);
