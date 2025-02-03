import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="flask_blog"
    )

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Utworzenie tabeli 'stats' jeśli nie istnieje
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            views INT NOT NULL
        )
    ''')
    print("Tabela 'stats' została utworzona (jeśli nie istniała).")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    print("Tabele zostały utworzone.")