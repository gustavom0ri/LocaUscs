import smtplib
import os
from email.message import EmailMessage

# Configurações do servidor SMTP
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = "gustavomori382@gmail.com"
PASSWORD = os.getenv("PASSWORD")

def enviar_email(destinatario, assunto, corpo):
    print(f"[LOG] Preparando para enviar email para {destinatario} com assunto '{assunto}'")
    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = USERNAME
    msg['To'] = destinatario
    msg.set_content(corpo)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(USERNAME, PASSWORD)
            smtp.send_message(msg)
        print(f"[LOG] Email enviado com sucesso para {destinatario}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar email para {destinatario}: {e}")

def email_negociacao_recebida(carro_id, dados):
    print(f"[LOG] email_negociacao_recebida chamado para carro_id={carro_id} com dados={dados}")
    assunto = f"Nova negociação para seu veículo {dados.get('veiculo', '')}"
    corpo = f"""
Olá,

Você recebeu uma nova proposta de negociação para o veículo {dados.get('veiculo', '')}.

Detalhes da negociação:
Nome: {dados.get('nome', '')}
Email: {dados.get('email', '')}
Telefone: {dados.get('telefone', '')}
WhatsApp: {dados.get('whatsapp', '')}
Mensagem: {dados.get('mensagem', '')}
Valor Proposto: {dados.get('valor_proposto', '')}
Duração do Aluguel: {dados.get('duracao', '')}
Local de Moradia: {dados.get('local', '')}

Por favor, acesse sua conta para responder ou atualizar o status da negociação.

Atenciosamente,
LocaUSCS
"""
    from locauscs import obter_email_dono_carro
    email_dono = obter_email_dono_carro(carro_id)
    if email_dono:
        print(f"[LOG] Email do dono do carro encontrado: {email_dono}")
        enviar_email(email_dono, assunto, corpo)
    else:
        print(f"[ERRO] Email do dono do carro não encontrado para carro_id={carro_id}")

def email_negociacao_criada(email_locatario, dados):
    print(f"[LOG] email_negociacao_criada chamado para email_locatario={email_locatario} com dados={dados}")
    assunto = f"Confirmação de negociação para {dados.get('veiculo', '')}"
    corpo = f"""
Olá,

Sua proposta de negociação para o veículo {dados.get('veiculo', '')} foi registrada com sucesso.

Você será informado sobre qualquer alteração no status da negociação.

Atenciosamente,
LocaUSCS
"""
    enviar_email(email_locatario, assunto, corpo)

def email_status_alterado(email_locatario, dados):
    print(f"[LOG] email_status_alterado chamado para email_locatario={email_locatario} com dados={dados}")
    assunto = f"Status da negociação atualizado para {dados.get('veiculo', '')}"
    corpo = f"""
Olá,

O status da sua negociação para o veículo {dados.get('veiculo', '')} foi alterado para: {dados.get('status', '')}.

Por favor, acesse sua conta para mais informações.

Atenciosamente,
LocaUSCS
"""
    enviar_email(email_locatario, assunto, corpo)

# Exemplos de funções de log para chamadas e envios relacionados à negociação

def log_chamada_negociacao_recebida(carro_id, dados):
    print(f"[LOG] Chamada recebida de negociação para carro_id={carro_id} com dados: {dados}")

def log_chamada_negociacao_enviada(carro_id, dados):
    print(f"[LOG] Chamada enviada de negociação para carro_id={carro_id} com dados: {dados}")

def log_negociacao_criada(negociacao_id, dados):
    print(f"[LOG] Negociação criada: ID={negociacao_id}, dados={dados}")

def log_status_alterado(negociacao_id, status_antigo, status_novo):
    print(f"[LOG] Status da negociação {negociacao_id} alterado de '{status_antigo}' para '{status_novo}'")

# Uso hipotético dos logs junto com as funções principais:
# (Você pode chamar esses logs dentro das funções onde fizer sentido)

# Exemplo:
# log_chamada_negociacao_recebida(carro_id, dados)
# email_negociacao_recebida(carro_id, dados)
