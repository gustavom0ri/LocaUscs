import smtplib
import os
from email.message import EmailMessage
from email.utils import make_msgid

# Configurações do servidor SMTP, usa o Email do Gustavo
# e para a senha não estar disponivel colocamos uma variavel de ambiente no Notebook e o Python pega de lá

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = "gustavomori382@gmail.com"
PASSWORD = os.getenv("PASSWORD")

# Caminhos absolutos das imagens
LOGO_PATH = r"C:\Users\gusta\PycharmProjects\LocaUscs\static\artes_visuais\locauscs_logo.png"
PATTERN_PATH = r"C:\Users\gusta\PycharmProjects\LocaUscs\static\artes_visuais\pattern-1.png"

# a função que envia o Email, colocamos varios logs que printam no console em que ponto do Emai esta para facilitar a correção de BUGS
def enviar_email(destinatario, assunto, corpo_html):
    print(f"[LOG] Preparando para enviar email para {destinatario} com assunto '{assunto}'")

    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = USERNAME
    msg['To'] = destinatario

    # Gerar Content-IDs únicos para as imagens
    logo_cid = make_msgid(domain='locauscs.com').strip('<>')
    pattern_cid = make_msgid(domain='locauscs.com').strip('<>')

    # Corpo HTML com as imagens referenciadas via cid:
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8" />
    <style>
      body {{
        background-color: #FFFAF0;
        margin: 0;
        padding: 0;
        font-family: 'Comic Sans MS', 'Arial Rounded MT Bold', cursive, sans-serif;
      }}
      .email-container {{
        background-color: white;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        max-width: 600px;
        margin: 40px auto;
        padding: 30px 20px;
        text-align: center;
      }}
      .logo {{
        max-width: 160px;
        margin-bottom: 20px;
      }}
      .content {{
        font-size: 16px;
        color: #444;
        margin-top: 10px;
        text-align: left;
        line-height: 1.6;
      }}
      .button {{
        display: inline-block;
        margin-top: 30px;
        padding: 12px 25px;
        background-color: #FF6B6B;
        color: white;
        text-decoration: none;
        border-radius: 25px;
        font-weight: bold;
        transition: background-color 0.3s ease;
      }}
      .button:hover {{
        background-color: #ff8787;
      }}
      .footer {{
        margin-top: 30px;
        font-size: 12px;
        color: #999;
      }}
    </style>
    </head>
    <body>
      <div class="email-container">
        <img src="cid:{logo_cid}" alt="LocaUSCS Logo" class="logo" />
        <div class="content">
          {corpo_html}
          <div style="text-align:center;">
            <a class="button" href="http://127.0.0.1:5000/negociacoes">Ver minhas negociações</a>
          </div>
        </div>
        <div class="footer">
          ❤️ Obrigado por usar o LocaUSCS!
        </div>
      </div>
    </body>
    </html>
    """

    msg.add_alternative(html, subtype='html')

    # Anexa a logo
    with open(LOGO_PATH, 'rb') as img:
        msg.get_payload()[0].add_related(img.read(), 'image', 'png', cid=logo_cid)

    # Anexa o pattern
    with open(PATTERN_PATH, 'rb') as img:
        msg.get_payload()[0].add_related(img.read(), 'image', 'png', cid=pattern_cid)

    #para garantir que o Email foi enviado
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(USERNAME, PASSWORD)
            smtp.send_message(msg)
        print(f"[LOG] Email enviado com sucesso para {destinatario}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar email para {destinatario}: {e}")

#função que envia o Email para o dono do carro, tambem contem logs para facilitar a correção de Erros
def email_negociacao_recebida(carro_id, dados):
    print(f"[LOG] email_negociacao_recebida chamado para carro_id={carro_id} com dados={dados}")
    assunto = f"Nova negociação para seu veículo {dados.get('veiculo', '')}"
    corpo_html = f"""
    <p>Olá,</p>
    <p>Você recebeu uma nova proposta de negociação para o veículo <strong>{dados.get('veiculo', '')}</strong>.</p>

    <p><strong>Detalhes da negociação:</strong><br>
    Nome: {dados.get('nome', '')}<br>
    Email: {dados.get('email', '')}<br>
    Telefone: {dados.get('telefone', '')}<br>
    WhatsApp: {dados.get('whatsapp', '')}<br>
    Mensagem: {dados.get('mensagem', '')}<br>
    Valor Proposto: {dados.get('valor_proposto', '')}<br>
    Duração do Aluguel: {dados.get('duracao', '')}<br>
    Local de Moradia: {dados.get('local', '')}
    </p>

    <p>Por favor, acesse sua conta para responder ou atualizar o status da negociação.</p>

    <p>Atenciosamente,<br>LocaUSCS</p>
    """

    from locauscs import obter_email_dono_carro
    email_dono = obter_email_dono_carro(carro_id)
    if email_dono:
        print(f"[LOG] Email do dono do carro encontrado: {email_dono}")
        enviar_email(email_dono, assunto, corpo_html)
    else:
        print(f"[ERRO] Email do dono do carro não encontrado para carro_id={carro_id}")

#função que envia o Email para o Criador da negociação, tambem contem logs para facilitar a correção de Erros
def email_negociacao_criada(email_locatario, dados):
    print(f"[LOG] email_negociacao_criada chamado para email_locatario={email_locatario} com dados={dados}")
    assunto = f"Confirmação de negociação para {dados.get('veiculo', '')}"
    corpo_html = f"""
    <p>Olá,</p>

    <p>Sua proposta de negociação para o veículo <strong>{dados.get('veiculo', '')}</strong> foi registrada com sucesso.</p>

    <p>Você será informado sobre qualquer alteração no status da negociação.</p>

    <p>Atenciosamente,<br>LocaUSCS</p>
    """
    enviar_email(email_locatario, assunto, corpo_html)

#função que envia o Email quando há alguma alteração de status, tambem contem logs para facilitar a correção de Erros, ainda não foi implementado nessa versão do Codigo
def email_status_alterado(email_locatario, dados):
    print(f"[LOG] email_status_alterado chamado para email_locatario={email_locatario} com dados={dados}")
    assunto = f"Status da negociação atualizado para {dados.get('veiculo', '')}"
    corpo_html = f"""
    <p>Olá,</p>

    <p>O status da sua negociação para o veículo <strong>{dados.get('veiculo', '')}</strong> foi alterado para: <strong>{dados.get('status', '')}</strong>.</p>

    <p>Por favor, acesse sua conta para mais informações.</p>

    <p>Atenciosamente,<br>LocaUSCS</p>
    """
    enviar_email(email_locatario, assunto, corpo_html)

# Funções de log (mantidas iguais)
def log_chamada_negociacao_recebida(carro_id, dados):
    print(f"[LOG] Chamada recebida de negociação para carro_id={carro_id} com dados: {dados}")

def log_chamada_negociacao_enviada(carro_id, dados):
    print(f"[LOG] Chamada enviada de negociação para carro_id={carro_id} com dados: {dados}")

def log_negociacao_criada(negociacao_id, dados):
    print(f"[LOG] Negociação criada: ID={negociacao_id}, dados={dados}")

def log_status_alterado(negociacao_id, status_antigo, status_novo):
    print(f"[LOG] Status da negociação {negociacao_id} alterado de '{status_antigo}' para '{status_novo}'")
