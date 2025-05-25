import smtplib
import ssl
import os


def enviar_email(mensagem):
    host = "smtp.gmail.com"
    port = 465
    username = "gustavomori382@gmail.com"
    password = os.getenv("PASSWORD")  # Certifique-se de definir a variável de ambiente PASSWORD
    receiver = "gustavomori382@gmail.com"  # Destinatário do e-mail
    context = ssl.create_default_context()

    # Adicionando o título conforme solicitado
    assunto = "Aviso! alguém está interessado em alugar o seu veículo"

    try:
        # Configurando o título e corpo do e-mail
        email_message = f"Subject: {assunto}\n\n{mensagem}"

        # Enviando o e-mail
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, receiver, email_message.encode("utf-8"))
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
