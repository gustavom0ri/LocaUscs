import sqlite3
import os

def corrigir_caminhos_imagens():
    try:
        conn = sqlite3.connect('locauscs.db')
        cursor = conn.cursor()

        # Seleciona todos os carros com imagem cadastrada
        cursor.execute("SELECT id, imagem FROM carros WHERE imagem IS NOT NULL")
        carros = cursor.fetchall()

        for carro in carros:
            id_carro, caminho_imagem = carro
            if '\\' in caminho_imagem or '/' in caminho_imagem:
                # Extrai apenas o nome do arquivo
                nome_arquivo = os.path.basename(caminho_imagem)
                print(f"Corrigindo ID {id_carro}: {caminho_imagem} → {nome_arquivo}")

                # Atualiza no banco
                cursor.execute("UPDATE carros SET imagem = ? WHERE id = ?", (nome_arquivo, id_carro))

        conn.commit()
        print("Caminhos corrigidos com sucesso.")
    except Exception as e:
        print("Erro:", e)
    finally:
        conn.close()

corrigir_caminhos_imagens()
