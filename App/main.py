from flask import Flask, render_template, redirect, request, session
from PIL import Image
import numpy as np
import tensorflow as tf
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
import os


app = Flask(__name__)
app.secret_key ="12bb2f7a8fae07f6a931b8e4c695b474"
app.secret_key = os.getenv("SECRET_KEY")
email_remetente = os.getenv("EMAIL_APP")
senha_email = os.getenv("EMAIL_PASSWORD")
def processaImagemDoUsuario(imagem):
    imagem = Image.open(imagem.stream).convert("RGB")
    imagem = imagem.resize((150, 150))
    imagem_array = np.array(imagem)/255
    return np.expand_dims(imagem_array, axis=0)

def enviaEmail(mensagem, destinatario, assunto = "RESULTADO DA ANALISE DO RAIO-X", remetente = email_remetente, senha = senha_email):
    mensagem_envio = EmailMessage()
    mensagem_envio["From"] = remetente
    mensagem_envio["To"] = destinatario
    mensagem_envio["Subject"] = assunto
    mensagem_envio.set_content(mensagem)

    contexto = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=contexto) as smtp:
        smtp.login(remetente, senha)
        smtp.send_message(mensagem_envio)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods =["POST"])
def uploadImage():
    session["nome"] = request.form.get("nome")
    session["email"] = request.form.get("email")
    session["cpf"] = request.form.get("cpf")
    return render_template("upload.html", nome = session["nome"].split()[0], email=session["email"])


@app.route("/processamento", methods=["POST"])
def processarImagem():
    imagem = request.files["raiox"]
    imagem_processada = processaImagemDoUsuario(imagem)
    previsao = modelo.predict(imagem_processada)
    mensagem = ""

    nome = session.get("nome")
    cpf = session.get("cpf")
    email = session.get("email")
    if previsao[0][0] >= 0.5:
        mensagem = f"""\
Prezado(a) {nome} (CPF: {cpf}),

Informamos que o resultado da análise do exame de raio-X indica a presença de pneumonia.
Recomendamos que procure atendimento médico especializado para avaliação e tratamento adequados.

Atenciosamente,
Equipe Médica
"""

        enviaEmail(mensagem, email)
    else:
        mensagem = f"""\
Prezado(a) {nome} (CPF: {cpf}),

Informamos que o resultado da análise do exame de raio-X não indica sinais de pneumonia.
Caso apresente sintomas ou dúvidas, sugerimos acompanhamento médico.

Atenciosamente,
Equipe Médica
"""

        enviaEmail(mensagem, email)
    return render_template("upload.html", mensagem = "Imagem enviada com sucesso! Em alguns segundos vc ira receber o resultado no seu e-mail")


if __name__ == "__main__":
    app.run(debug=True)