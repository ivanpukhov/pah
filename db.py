import sqlite3


def create_orders_table():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       date TEXT,
                       time TEXT,
                       address TEXT,
                       acreage INTEGER,
                       phone_number TEXT)
                   """)
    conn.commit()
    conn.close()


def add_order(date, time, address, acreage, phone_number):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (date, time, address, acreage, phone_number) VALUES (?, ?, ?, ?, ?)",
                   (date, time, address, acreage, phone_number))
    conn.commit()
    conn.close()


#
# def get_all_orders():
#     conn = sqlite3.connect("orders.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM orders")
#     orders = cursor.fetchall()
#     conn.close()
#     return orders


def get_order_dates(date):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE date = ?", (date,))
    orders = cursor.fetchall()
    conn.close()
    return orders


def get_order_dates_list():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, COUNT(*) FROM orders GROUP BY date ORDER BY date ASC")
    dates = cursor.fetchall()
    conn.close()

    dates.sort(key=lambda x: x[0])

    return dates


create_orders_table()
