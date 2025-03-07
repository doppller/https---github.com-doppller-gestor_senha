from flask import Flask, render_template, request, redirect, session, url_for, flash
from bcrypt import hashpw, checkpw, gensalt
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

# Simulando um banco de dados (dicionário)
usuarios = {}
senhas = {}

# Gerar chave de criptografia para o cofre
chave = Fernet.generate_key()
cifra = Fernet(chave)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"].encode()
        hash_senha = hashpw(senha, gensalt())
        usuarios[usuario] = hash_senha
        return redirect(url_for("login"))
    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"].encode()

        if usuario in usuarios and checkpw(senha, usuarios[usuario]):
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))  # Login bem-sucedido, redireciona para o dashboard
        
        flash("Login inválido! Verifique suas credenciais.", "error")  # Mensagem de erro
        return redirect(url_for("login"))  # Redireciona para a tela de login

    return render_template("login.html")  # Renderiza a tela de login


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

    return render_template("dashboard.html", senhas=senhas)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
