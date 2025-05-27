import sqlite3

def listar_tabelas(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()
    print("Tabelas no banco:")
    for tabela in tabelas:
        print(tabela[0])
    conn.close()

if __name__ == "__main__":
    listar_tabelas("../locauscs.db")
