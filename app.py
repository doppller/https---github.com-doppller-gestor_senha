import os
import csv
from flask import Flask, render_template, request, redirect, session, url_for, flash, Response
from bcrypt import hashpw, checkpw, gensalt
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

# Verifica se já existe uma chave de criptografia salva
if os.path.exists("chave.key"):
    with open("chave.key", "rb") as key_file:
        chave = key_file.read()
else:
    chave = Fernet.generate_key()
    with open("chave.key", "wb") as key_file:
        key_file.write(chave)

cifra = Fernet(chave)

# Simulação de banco de dados de usuários (armazenados com hash seguro)
usuarios = {
    "admin": hashpw("12345".encode(), gensalt())  # Senha segura do admin
}

# Simulação de armazenamento de senhas (Plataforma -> (Usuário, Senha Criptografada))
senhas = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"].encode()

        if usuario in usuarios:
            flash("Usuário já existe!", "error")
            return redirect(url_for("cadastro"))

        hash_senha = hashpw(senha, gensalt())
        usuarios[usuario] = hash_senha
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario in usuarios and checkpw(senha.encode(), usuarios[usuario]):
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha inválidos")  # Isso aparece no HTML

    return render_template("login.html")


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

    # Descriptografar as senhas antes de enviar para o frontend
    senhas_descriptografadas = {
        plataforma: (dados[0], cifra.decrypt(dados[1].encode()).decode())
        for plataforma, dados in senhas.items()
    }

    return render_template("dashboard.html", senhas=senhas_descriptografadas)

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

    return Response(gerar_csv(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=senhas.csv"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
