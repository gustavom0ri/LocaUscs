import re

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
        "mensagem": r"Mensagem:\s*(.*)",  # mensagem pode estar vazia
    }

    for chave, padrao in padroes.items():
        resultado = re.search(padrao, descricao)
        if resultado:
            campos[chave] = resultado.group(1).strip()

    return campos
