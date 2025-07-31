from flask import Flask, render_template, request, redirect, session
import psycopg2
import hashlib

app = Flask(__name__)
app.secret_key = 'rahasia'  # Ganti sesuai kebutuhan

# Konfigurasi database PostgreSQL
db_conn = psycopg2.connect(
    host=os.environ['PGHOST'],
    dbname=os.environ['PGDATABASE'],
    user=os.environ['PGUSER'],        # Ganti sesuai user DB kamu
    password=os.environ['PGPASSWORD'],     # Ganti sesuai password DB kamu
    port=os.environt['PGPORT']
)

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        cur = db_conn.cursor()
        cur.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = username
            session['role'] = user[0]
            return redirect('/dashboard')

        return "Login gagal. Username atau password salah."

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        cur = db_conn.cursor()

        # Cek apakah username sudah ada
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            return "Username sudah digunakan. Silakan pilih username lain."

        # Simpan user baru
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, 'user'))
        db_conn.commit()
        cur.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    
    if session['role'] == 'admin':
        return f"<h1>Selamat datang Admin {session['username']}</h1>"
    return f"<h1>Selamat datang User {session['username']}</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
