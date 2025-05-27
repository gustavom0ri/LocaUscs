import sqlite3

# Caminho para o banco de dados
caminho_db = 'locauscs.db'

# Conexão com o banco de dados
conexao = sqlite3.connect(caminho_db)
cursor = conexao.cursor()

# Consulta para obter todos os dados da tabela carros
cursor.execute("SELECT * FROM carros")
carros = cursor.fetchall()

# Pegando os nomes das colunas
colunas = [descricao[0] for descricao in cursor.description]

# Imprime os nomes das colunas
print("Colunas da tabela 'carros':")
print(colunas)
print("-" * 40)

# Imprime cada registro com as colunas
for carro in carros:
    for nome_coluna, valor in zip(colunas, carro):
        print(f"{nome_coluna}: {valor}")
    print("-" * 40)

# Fecha a conexão
conexao.close()
