import sqlite3

# Caminho para o seu banco de dados
db_path = r"/locauscs.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Tenta adicionar a coluna 'status' à tabela 'negociacoes'
    cursor.execute("ALTER TABLE negociacoes ADD COLUMN status TEXT")
    print("Coluna 'status' adicionada com sucesso.")
except sqlite3.OperationalError as e:
    # Se a coluna já existir, vai lançar um erro, você pode ignorar ou mostrar
    print("Erro ao adicionar coluna:", e)

conn.commit()
conn.close()
