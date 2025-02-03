import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="flask_blog"
    )

def update_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sprawdzenie, czy kolumna 'role' istnieje
    cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(255)")
        print("Kolumna 'role' została dodana do tabeli 'users'.")

    # Sprawdzenie, czy kolumna 'email' istnieje
    cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
        print("Kolumna 'email' została dodana do tabeli 'users'.")

    # Sprawdzenie, czy kolumna 'first_name' istnieje
    cursor.execute("SHOW COLUMNS FROM users LIKE 'first_name'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("ALTER TABLE users ADD COLUMN first_name VARCHAR(255)")
        print("Kolumna 'first_name' została dodana do tabeli 'users'.")

    # Sprawdzenie, czy kolumna 'last_name' istnieje
    cursor.execute("SHOW COLUMNS FROM users LIKE 'last_name'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("ALTER TABLE users ADD COLUMN last_name VARCHAR(255)")
        print("Kolumna 'last_name' została dodana do tabeli 'users'.")

    # Sprawdzenie, czy kolumna 'phone_number' istnieje
    cursor.execute("SHOW COLUMNS FROM users LIKE 'phone_number'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("ALTER TABLE users ADD COLUMN phone_number VARCHAR(255)")
        print("Kolumna 'phone_number' została dodana do tabeli 'users'.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_users_table()
    print("Tabela 'users' została zaktualizowana.")