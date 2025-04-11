
import os
import secrets
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, Response
from bcrypt import hashpw, checkpw, gensalt
from cryptography.fernet import Fernet

app = Flask(__name__)

# Configurações de segurança melhoradas
app.secret_key = secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Gerenciamento de chave de criptografia
if not os.path.exists('secret_key.key'):
    with open('secret_key.key', 'wb') as key_file:
        key_file.write(Fernet.generate_key())

with open('secret_key.key', 'rb') as key_file:
    chave = key_file.read()

cifra = Fernet(chave)

# Banco de dados temporário
usuarios = {}
senhas = {}

# ==============================================
# Rotas Principais
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

        if usuario in usuarios and checkpw(senha.encode(), usuarios[usuario]):
            session["usuario"] = usuario
            session.permanent = True
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

        if usuario in usuarios:
            flash("Usuário já existe", "error")
            return redirect(url_for("cadastro"))

        if senha != confirmar_senha:
            flash("As senhas não coincidem", "error")
            return redirect(url_for("cadastro"))

        if len(senha) < 8:
            flash("A senha deve ter pelo menos 8 caracteres", "error")
            return redirect(url_for("cadastro"))

        hash_senha = hashpw(senha.encode(), gensalt())
        usuarios[usuario] = hash_senha
        flash("Cadastro realizado! Faça login", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        plataforma = request.form["plataforma"]
        user = request.form["user"]
        senha = request.form["senha"].encode()
        senha_criptografada = cifra.encrypt(senha).decode()
        senhas[plataforma] = (user, senha_criptografada)
        flash("Senha adicionada com sucesso!", "success")

    senhas_descriptografadas = {
        plataforma: (dados[0], cifra.decrypt(dados[1].encode()).decode())
        for plataforma, dados in senhas.items()
    }

    return render_template("dashboard.html", usuario=session["usuario"], senhas=senhas_descriptografadas)

# ==============================================
# APIs e Funcionalidades Adicionais
# ==============================================

@app.route("/check_username", methods=["POST"])
def check_username():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Nome de usuário não fornecido"}), 400
    return jsonify({"available": username not in usuarios})

@app.route("/get_password")
def get_password():
    if "usuario" not in session:
        return jsonify({"error": "Não autorizado"}), 401

    plataforma = request.args.get("plataforma")
    if not plataforma or plataforma not in senhas:
        return jsonify({"error": "Plataforma não encontrada"}), 404

    try:
        senha_decrypt = cifra.decrypt(senhas[plataforma][1].encode()).decode()
        return jsonify({"senha": senha_decrypt})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gerar_senha")
def gerar_senha():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("gerar_senha.html")

@app.route("/download_senhas")
def download_senhas():
    if "usuario" not in session:
        flash("Você precisa estar logado para baixar suas senhas.", "error")
        return redirect(url_for("login"))

    def gerar_csv():
        yield "Plataforma,Usuário,Senha\n"
        for plataforma, dados in senhas.items():
            user, senha_criptografada = dados
            senha_real = cifra.decrypt(senha_criptografada.encode()).decode()
            yield f"{plataforma},{user},{senha_real}\n"

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
# Configurações e Execução
# ==============================================

if __name__ == "__main__":
    app.run(ssl_context='adhoc')
