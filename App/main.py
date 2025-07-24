#Biblioteca principal para  a API
from flask import Flask, render_template, redirect, request, session

#Processamento da imagem recebida do usuário
from PIL import Image
import numpy as np

#Carregar o modelo salvo
import tensorflow as tf

#Gerenciar o envio do email para o usuario
import smtplib
import ssl
from email.message import EmailMessage

#Carregar as chaves da api do flask
from dotenv import load_dotenv
import os


app = Flask(__name__)

modelo = tf.keras.models.load_model("App/Model/modelo_completo1.h5")
app.secret_key = os.getenv("SECRET_KEY")
email_remetente = os.getenv("EMAIL_APP")
senha_email = os.getenv("EMAIL_PASSWORD")

#Função para processar a imagem
def processaImagemDoUsuario(imagem):
    imagem = Image.open(imagem.stream).convert("RGB")
    imagem = imagem.resize((150, 150))
    imagem_array = np.array(imagem)/255
    return np.expand_dims(imagem_array, axis=0)

#Função que gerencia o envio do email
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