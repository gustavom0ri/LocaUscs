import sqlite3

# Caminho do banco de dados
db_path = '../locauscs.db'

# Conexão com o banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Renomear tabela antiga
    cursor.execute("ALTER TABLE negociacoes RENAME TO negociacoes_old")

    # 2. Criar nova tabela sem NOT NULL em 'descricao'
    cursor.execute("""
        CREATE TABLE negociacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carro_id INTEGER,
            descricao TEXT, -- agora permite NULL
            email_contato TEXT NOT NULL,
            telefone TEXT NOT NULL,
            FOREIGN KEY(carro_id) REFERENCES carros(id)
        )
    """)

    # 3. Copiar dados da tabela antiga para a nova
    cursor.execute("""
        INSERT INTO negociacoes (id, carro_id, descricao, email_contato, telefone)
        SELECT id, carro_id, descricao, email_contato, telefone FROM negociacoes_old
    """)

    # 4. Excluir a tabela antiga
    cursor.execute("DROP TABLE negociacoes_old")

    # Salvar alterações
    conn.commit()
    print("Tabela negociacoes atualizada com sucesso!")
except sqlite3.Error as e:
    print(f"Erro ao modificar a tabela: {e}")
    conn.rollback()
finally:
    conn.close()
