import sqlite3
import re

# Conexão com o banco
conn = sqlite3.connect("locauscs.db")  # substitua pelo nome do seu banco
cursor = conn.cursor()

# Função para extrair os dados da descrição
def extrair_dados(descricao):
    campos = {
        "nome": "",
        "duracao": "",
        "moradia": "",
        "valor": "",
        "whatsapp": "",
        "mensagem": ""
    }

    padroes = {
        "nome": r"Nome:\s*(.+)",
        "duracao": r"Duração do Aluguel:\s*(.+)",
        "moradia": r"Local de Moradia:\s*(.+)",
        "valor": r"Valor Proposto:\s*(.+)",
        "whatsapp": r"WhatsApp:\s*(.+)",
        "mensagem": r"Mensagem:\s*(.*)",
    }

    for chave, padrao in padroes.items():
        resultado = re.search(padrao, descricao)
        if resultado:
            campos[chave] = resultado.group(1).strip()

    return campos

# Consulta à tabela
cursor.execute("SELECT id, carro_id, descricao, email_contato, telefone, status FROM negociacoes")
negociacoes = cursor.fetchall()

# Exibindo ordenação das colunas
print("ORDENAÇÃO DAS COLUNAS:")
print("0 - id")
print("1 - carro_id")
print("2 - descricao")
print("3 - email_contato")
print("4 - telefone")
print("5 - status\n")

# Exibindo dados com extração
print("EXEMPLOS DE DADOS FORMATADOS:")
for negociacao in negociacoes:
    id_, carro_id, descricao, email_contato, telefone, status = negociacao
    dados_extraidos = extrair_dados(descricao)

    print(f"ID: {id_}")
    print(f"Carro ID: {carro_id}")
    print(f"Nome: {dados_extraidos['nome']}")
    print(f"Duração: {dados_extraidos['duracao']}")
    print(f"Local de Moradia: {dados_extraidos['moradia']}")
    print(f"Valor Proposto: {dados_extraidos['valor']}")
    print(f"WhatsApp: {dados_extraidos['whatsapp']}")
    print(f"Mensagem: {dados_extraidos['mensagem']}")
    print(f"E-mail: {email_contato}")
    print(f"Telefone: {telefone}")
    print(f"Status: {status}")
    print("-" * 50)

# Fecha a conexão
conn.close()
