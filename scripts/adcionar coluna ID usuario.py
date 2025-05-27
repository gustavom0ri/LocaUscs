import sqlite3

def adicionar_coluna():
    try:
        conn = sqlite3.connect("../locauscs.db")
        cursor = conn.cursor()
        # Adiciona a coluna id_usuario do tipo INTEGER (ou conforme a necessidade)
        cursor.execute("ALTER TABLE carros ADD COLUMN id_usuario INTEGER")
        conn.commit()
        print("Coluna 'id_usuario' adicionada com sucesso!")
    except sqlite3.OperationalError as e:
        print(f"Erro ao adicionar coluna: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    adicionar_coluna()
