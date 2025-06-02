from flask import Flask, render_template, request, redirect
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

def init_db():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não configurada no ambiente.")
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    theme TEXT DEFAULT 'emo1'
                )
            ''')
            conn.commit()

@app.route('/')
def index():
    if not DATABASE_URL:
        return "Erro: DATABASE_URL não configurada.", 500
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT content, theme FROM messages ORDER BY id DESC")
            messages = cur.fetchall()
    return render_template('index.html', messages=messages)

@app.route('/enviar', methods=['POST'])
def enviar():
    content = request.form['message'].strip()
    theme = request.form.get('theme', 'emo1')
    if content:
        with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO messages (content, theme) VALUES (%s, %s)", (content, theme))
                conn.commit()
    return redirect('/')

if __name__ == '__main__':
    init_db()  # execute só 1 vez para criar tabela localmente
    app.run(debug=True)
