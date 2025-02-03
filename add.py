import mysql.connector
from werkzeug.security import generate_password_hash

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="flask_blog"
    )

def add_admin_user():
    username = 'admin1'
    password = 'admin1'
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            phone_number VARCHAR(255),
            role VARCHAR(255)
        )
    ''')
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                   (username, hashed_password, 'admin'))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_admin_user()
    print("Użytkownik admin1 został dodany do bazy danych.")