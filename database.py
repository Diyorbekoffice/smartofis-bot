import sqlite3
from config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        telegram_id INTEGER UNIQUE,
        work_start TEXT,
        work_end TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        checkin_time TEXT,
        checkout_time TEXT,
        source TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        text TEXT,
        time TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        text TEXT,
        time TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        type TEXT,
        amount INTEGER,
        reason TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )""")
    conn.commit()
    conn.close()

def add_employee(name, telegram_id, work_start, work_end):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO employees (name, telegram_id, work_start, work_end) VALUES (?, ?, ?, ?)",
                 (name, telegram_id, work_start, work_end))
    conn.commit()
    conn.close()

def get_employee_by_telegram_id(telegram_id):
    conn = get_db()
    cur = conn.execute("SELECT * FROM employees WHERE telegram_id = ?", (telegram_id,))
    emp = cur.fetchone()
    conn.close()
    return emp

def log_checkin(employee_id, date, checkin_time, source='bot'):
    conn = get_db()
    conn.execute(
        "INSERT INTO attendance (employee_id, date, checkin_time, source) VALUES (?, ?, ?, ?)",
        (employee_id, date, checkin_time, source)
    )
    conn.commit()
    conn.close()

def log_checkout(employee_id, date, checkout_time, source='bot'):
    conn = get_db()
    conn.execute(
        "UPDATE attendance SET checkout_time=?, source=? WHERE employee_id=? AND date=?",
        (checkout_time, source, employee_id, date)
    )
    conn.commit()
    conn.close()

def submit_plan(employee_id, date, text, time):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO plans (employee_id, date, text, time) VALUES (?, ?, ?, ?)",
        (employee_id, date, text, time)
    )
    conn.commit()
    conn.close()

def submit_report(employee_id, date, text, time):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO reports (employee_id, date, text, time) VALUES (?, ?, ?, ?)",
        (employee_id, date, text, time)
    )
    conn.commit()
    conn.close()

def add_fine(employee_id, date, fine_type, amount, reason):
    conn = get_db()
    conn.execute(
        "INSERT INTO fines (employee_id, date, type, amount, reason) VALUES (?, ?, ?, ?, ?)",
        (employee_id, date, fine_type, amount, reason)
    )
    conn.commit()
    conn.close()

def get_fines_by_employee(employee_id, month=None):
    conn = get_db()
    if month:
        cur = conn.execute(
            "SELECT * FROM fines WHERE employee_id=? AND strftime('%Y-%m', date)=?",
            (employee_id, month)
        )
    else:
        cur = conn.execute(
            "SELECT * FROM fines WHERE employee_id=?",
            (employee_id,)
        )
    fines = cur.fetchall()
    conn.close()
    return fines

def get_all_employees():
    conn = get_db()
    cur = conn.execute("SELECT * FROM employees")
    emps = cur.fetchall()
    conn.close()
    return emps

def get_daily_summary(date):
    conn = get_db()
    cur = conn.execute("""
        SELECT e.name, f.type, f.amount, f.reason FROM fines f
        JOIN employees e ON f.employee_id = e.id
        WHERE f.date = ?
    """, (date,))
    summary = cur.fetchall()
    conn.close()
    return summary
