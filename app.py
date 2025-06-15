import os
import secrets
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, Response
from bcrypt import hashpw, checkpw, gensalt
from cryptography.fernet import Fernet

app = Flask(__name__)

# ==============================================
# Configurações
# ==============================================
app.secret_key = secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Criptografia
if not os.path.exists('secret_key.key'):
    with open('secret_key.key', 'wb') as key_file:
        key_file.write(Fernet.generate_key())

with open('secret_key.key', 'rb') as key_file:
    chave = key_file.read()
cifra = Fernet(chave)

# Banco de Dados
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permite acesso aos campos por nome
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            hash_senha TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            plataforma TEXT NOT NULL,
            username TEXT NOT NULL,
            senha_criptografada TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Executa ao iniciar a aplicação

# ==============================================
# Rotas do Front-End (HTML)
# ==============================================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if not usuario or not senha:
            flash("Preencha todos os campos", "error")
            return redirect(url_for("login"))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT hash_senha FROM usuarios WHERE usuario = ?', (usuario,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado and checkpw(senha.encode(), resultado['hash_senha'].encode()):
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha inválidos", "error")

    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")

        if not all([usuario, senha, confirmar_senha]):
            flash("Preencha todos os campos", "error")
            return redirect(url_for("cadastro"))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT usuario FROM usuarios WHERE usuario = ?', (usuario,))
        if cursor.fetchone():
            flash("Usuário já existe", "error")
            conn.close()
            return redirect(url_for("cadastro"))

        if senha != confirmar_senha:
            flash("As senhas não coincidem", "error")
            conn.close()
            return redirect(url_for("cadastro"))

        if len(senha) < 8:
            flash("A senha deve ter pelo menos 8 caracteres", "error")
            conn.close()
            return redirect(url_for("cadastro"))

        hash_senha = hashpw(senha.encode(), gensalt())
        cursor.execute(
            'INSERT INTO usuarios (usuario, hash_senha) VALUES (?, ?)',
            (usuario, hash_senha.decode())
        )
        conn.commit()
        conn.close()
        flash("Cadastro realizado! Faça login", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT plataforma, username, senha_criptografada 
        FROM senhas 
        WHERE usuario_id = (
            SELECT id FROM usuarios WHERE usuario = ?
        )
    ''', (session["usuario"],))
    senhas_db = cursor.fetchall()
    conn.close()

    senhas_descriptografadas = {
        item['plataforma']: (
            item['username'], 
            cifra.decrypt(item['senha_criptografada'].encode()).decode()
        )
        for item in senhas_db
    }
    return render_template("dashboard.html", 
        usuario=session["usuario"], 
        senhas=senhas_descriptografadas
    )

# ==============================================
# API RESTful (Para o Front-End JS)
# ==============================================
@app.route("/api/senhas", methods=["GET"])
def api_get_senhas():
    if "usuario" not in session:
        return jsonify({"error": "Não autorizado"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, plataforma, username, senha_criptografada 
        FROM senhas 
        WHERE usuario_id = (
            SELECT id FROM usuarios WHERE usuario = ?
        )
    ''', (session["usuario"],))
    senhas_db = cursor.fetchall()
    conn.close()

    senhas_formatadas = [
        {
            "id": item['id'],
            "plataforma": item['plataforma'],
            "username": item['username'],
            "senha": cifra.decrypt(item['senha_criptografada'].encode()).decode()
        }
        for item in senhas_db
    ]
    return jsonify(senhas_formatadas)

@app.route("/api/senhas", methods=["POST"])
def api_add_senha():
    if "usuario" not in session:
        return jsonify({"error": "Não autorizado"}), 401

    data = request.json
    if not all([data.get("plataforma"), data.get("username"), data.get("senha")]):
        return jsonify({"error": "Dados incompletos"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM usuarios WHERE usuario = ?', (session["usuario"],))
    usuario_id = cursor.fetchone()['id']

    senha_criptografada = cifra.encrypt(data["senha"].encode()).decode()
    cursor.execute(
        '''INSERT INTO senhas 
           (usuario_id, plataforma, username, senha_criptografada) 
           VALUES (?, ?, ?, ?)''',
        (usuario_id, data["plataforma"], data["username"], senha_criptografada)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 201

@app.route("/api/senhas/<int:id>", methods=["DELETE"])
def api_delete_senha(id):
    if "usuario" not in session:
        return jsonify({"error": "Não autorizado"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM senhas 
        WHERE id = ? AND usuario_id = (
            SELECT id FROM usuarios WHERE usuario = ?
        )
    ''', (id, session["usuario"]))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return jsonify({"success": deleted}), 200 if deleted else 404

# ==============================================
# Rotas Adicionais (Download, Logout, etc.)
# ==============================================
@app.route("/download_senhas")
def download_senhas():
    if "usuario" not in session:
        return jsonify({"error": "Não autorizado"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT plataforma, username, senha_criptografada 
        FROM senhas 
        WHERE usuario_id = (
            SELECT id FROM usuarios WHERE usuario = ?
        )
    ''', (session["usuario"],))
    senhas_db = cursor.fetchall()
    conn.close()

    def gerar_csv():
        yield "Plataforma,Usuário,Senha\n"
        for item in senhas_db:
            senha_real = cifra.decrypt(item['senha_criptografada'].encode()).decode()
            yield f"{item['plataforma']},{item['username']},{senha_real}\n"

    return Response(
        gerar_csv(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=senhas.csv"}
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ==============================================
# Inicialização
# ==============================================
if __name__ == "__main__":
    app.run(ssl_context='adhoc')