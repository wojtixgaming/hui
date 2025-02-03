from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from functools import wraps
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'
entries = []
enazwa = ""
views = 0

# Połączenie z bazą danych SQLite
def get_db_connection():
    conn = sqlite3.connect('flask_blog.db')
    conn.row_factory = sqlite3.Row
    return conn

# Dekorator sprawdzający logowanie
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('logowanie'))
        return f(*args, **kwargs)
    return decorated_function

# Logowanie użytkownika
@app.route('/logowanie', methods=['GET', 'POST'])
def logowanie():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('panel'))
    return render_template("login.html")

# Wylogowanie użytkownika
@app.route('/wylogowanie')
def wylogowanie():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('logowanie'))

# Panel admina z listą wpisów
@app.route('/panel')
@login_required
def panel():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY date DESC")
    posts = cursor.fetchall()

    today = datetime.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT views FROM stats WHERE date=?", (today,))
    result = cursor.fetchone()
    if result:
        views = result['views']
    else:
        views = 0

    conn.close()
    return render_template("panel.html", posts=posts, views=views, username=session.get('username'))

# Strona główna z wpisami
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY date DESC")
    posts = cursor.fetchall()
    conn.close()
    return render_template("index.html", posts=posts)

# Statystyki
@app.route('/stats')
@login_required
def stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stats ORDER BY date DESC LIMIT 30")
    stats = cursor.fetchall()
    conn.close()
    return render_template("statystyki.html", stats=stats, username=session.get('username'))

# Pobieranie i zapisywanie danych o ruchu
@app.route('/get_traffic_data')
@login_required
def get_traffic_data():
    timeframe = request.args.get('timeframe', 'month')  # Domyślnie: miesiąc
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.today().strftime("%Y-%m-%d")

    # Sprawdzamy, czy są już statystyki dla dzisiejszego dnia
    cursor.execute("SELECT views FROM stats WHERE date=?", (today,))
    result = cursor.fetchone()

    if result:
        views = result['views'] + 1 
        cursor.execute("UPDATE stats SET views=? WHERE date=?", (views, today))
    else:
        views = 1
        cursor.execute("INSERT INTO stats (date, views) VALUES (?, ?)", (today, views))

    conn.commit()

    if timeframe == 'day':
        cursor.execute("SELECT date, views FROM stats ORDER BY date DESC LIMIT 1")
    elif timeframe == 'week':
        cursor.execute("SELECT date, views FROM stats ORDER BY date DESC LIMIT 7")
    elif timeframe == 'month':
        cursor.execute("SELECT date, views FROM stats ORDER BY date DESC LIMIT 30")
    elif timeframe == 'year':
        cursor.execute("SELECT date, views FROM stats ORDER BY date DESC LIMIT 365")
    else:
        conn.close()
        return jsonify({"error": "Nieprawidłowy okres"}), 400

    data = cursor.fetchall()
    conn.close()

    labels = [row['date'] for row in data]
    views = [row['views'] for row in data]

    return jsonify({"labels": labels, "views": views})

@app.route('/uzytkownicy', methods=['GET', 'POST'])
@login_required
def uzytkownicy():
    if request.method == 'POST':
        action = request.form.get('action')     
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        role = request.form.get('role')
        user_id = request.form.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        if action == 'add':
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password, email, first_name, last_name, phone_number, role) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                           (username, hashed_password, email, first_name, last_name, phone_number, role))
        elif action == 'edit':
            update_fields = []
            update_values = []
            if username:
                update_fields.append("username=?")
                update_values.append(username)
            if password:
                hashed_password = generate_password_hash(password)
                update_fields.append("password=?")
                update_values.append(hashed_password)
            if email:
                update_fields.append("email=?")
                update_values.append(email)
            if first_name:
                update_fields.append("first_name=?")
                update_values.append(first_name)
            if last_name:
                update_fields.append("last_name=?")
                update_values.append(last_name)
            if phone_number:
                update_fields.append("phone_number=?")
                update_values.append(phone_number)
            if role:
                update_fields.append("role=?")
                update_values.append(role)
            update_values.append(user_id)
            cursor.execute(f"UPDATE users SET {', '.join(update_fields)} WHERE id=?", update_values)
        elif action == 'delete':
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, first_name, last_name, phone_number, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template("uzytkownicy.html", users=users, username=session.get('username'))

@app.route('/wpisy')
@login_required
def wpisy():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Pobieramy wszystkie wpisy z bazy
    cursor.execute("SELECT id, title, slug, date FROM posts ORDER BY date DESC")
    posts = cursor.fetchall()

    conn.close()

    return render_template("wpisy.html", posts=posts, username=session.get('username'))

# 🔹 Dodawanie wpisu


# Funkcja do generowania slugów z tytułu
def generate_slug(title):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    return slug

@app.route('/add-entry', methods=['POST'])
@login_required
def add_entry():
    try:
        # Pobieranie danych z formularza
        title = request.form.get('title', '').strip()
        content = request.form.get('entry', '').strip()  # Pobierz treść wpisu
        if not title or not content:
            return "Błąd: Tytuł i treść wpisu są wymagane!", 400
        if title == "Wpis testowy":
            return "Błąd: Tytuł 'Wpis testowy' jest zarezerwowany!", 400
        
        slug = generate_slug(title)  # Tworzymy unikalny slug

        # Połączenie z bazą danych
        conn = get_db_connection()
        cursor = conn.cursor()

        # Sprawdzenie, czy slug już istnieje (zapobieganie duplikatom)
        cursor.execute("SELECT COUNT(*) FROM posts WHERE slug=?", (slug,))
        if cursor.fetchone()[0] > 0:
            slug += "-1"  # Dodanie sufiksu, jeśli slug już istnieje

        # Dodawanie nowego wpisu do bazy danych
        cursor.execute("INSERT INTO posts (title, content, slug) VALUES (?, ?, ?)", (title, content, slug))

        # Zatwierdzanie zmian
        conn.commit()
        conn.close()

        return redirect(url_for('wpisy'))

    except Exception as e:
        return f"Wystąpił błąd: {e}", 500

# 🔹 Usuwanie wpisu
@app.route('/usun-wpis/<int:post_id>', methods=['POST'])
@login_required
def usun_wpis(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Usunięcie wpisu o podanym ID
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('wpisy'))

@app.route('/wpis/<slug>')
def open_post(slug):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE slug=?", (slug,))
    post = cursor.fetchone()
    conn.close()
    
    if post:
        return render_template('post.html', post=post)
    else:
        return "Wpis nie istnieje", 404



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=201533)