import sqlite3
import hashlib
import os
import shutil

# Configuração do banco
db_path = '../locauscs.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Função para hash de senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Criar a tabela usuarios (caso não exista)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        senha TEXT
    )
""")

# Criar a tabela carros (caso não exista)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS carros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        modelo TEXT,
        ano INTEGER,
        km INTEGER,
        lkm INTEGER,
        categoria TEXT,
        imagem TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
""")

# Criar usuário "gusmori"
username = "gusmori"
email = "gustavomori382@gmail.com"
senha = hash_senha("1234")

cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, email, senha) VALUES (?, ?, ?)", (username, email, senha))
    conn.commit()
    print("Usuário gusmori criado.")

# Obter ID do usuário
cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
user_id = cursor.fetchone()[0]

# Lista de carros para inserir
carros = [
    {"modelo": "Fiat Uno", "ano": 2015, "km": 50000, "lkm": 12, "categoria": "popular", "imagem": "uno.jpg"},
    {"modelo": "Volkswagen Gol", "ano": 2016, "km": 40000, "lkm": 11, "categoria": "popular", "imagem": "gol.jpg"},
    {"modelo": "Ford Ka", "ano": 2017, "km": 45000, "lkm": 13, "categoria": "popular", "imagem": "ka.jpg"},
    {"modelo": "Chevrolet Onix", "ano": 2018, "km": 30000, "lkm": 14, "categoria": "popular", "imagem": "onix.jpg"},
    {"modelo": "Renault Kwid", "ano": 2019, "km": 25000, "lkm": 15, "categoria": "popular", "imagem": "kwid.jpg"},
    {"modelo": "Hyundai HB20", "ano": 2020, "km": 22000, "lkm": 13, "categoria": "popular", "imagem": "hb20.jpg"},
    {"modelo": "Toyota Etios", "ano": 2020, "km": 27000, "lkm": 14, "categoria": "popular", "imagem": "etios.jpg"},
    {"modelo": "Peugeot 208", "ano": 2021, "km": 19000, "lkm": 13, "categoria": "popular", "imagem": "208.jpg"},
    {"modelo": "Fiat Argo", "ano": 2022, "km": 15000, "lkm": 13, "categoria": "popular", "imagem": "argo.jpg"},
    {"modelo": "Chevrolet Corsa", "ano": 2012, "km": 80000, "lkm": 10, "categoria": "popular", "imagem": "corsa.jpg"},
    {"modelo": "BMW Série 3", "ano": 2019, "km": 30000, "lkm": 9, "categoria": "luxo", "imagem": "bmw.jpg"},
    {"modelo": "Mercedes-Benz C180", "ano": 2020, "km": 20000, "lkm": 8, "categoria": "luxo", "imagem": "mercedes.jpg"},
    {"modelo": "Audi A4", "ano": 2021, "km": 15000, "lkm": 10, "categoria": "luxo", "imagem": "audi.jpg"},
    {"modelo": "Volvo S60", "ano": 2018, "km": 35000, "lkm": 9, "categoria": "luxo", "imagem": "volvo.jpg"},
    {"modelo": "Jaguar XE", "ano": 2017, "km": 40000, "lkm": 8, "categoria": "luxo", "imagem": "jaguar.jpg"},
    {"modelo": "Lexus IS", "ano": 2016, "km": 45000, "lkm": 10, "categoria": "luxo", "imagem": "lexus.jpg"},
    {"modelo": "Porsche Panamera", "ano": 2022, "km": 10000, "lkm": 7, "categoria": "luxo", "imagem": "panamera.jpg"},
    {"modelo": "Tesla Model S", "ano": 2021, "km": 12000, "lkm": 0, "categoria": "luxo", "imagem": "tesla.jpg"},
    {"modelo": "Land Rover Evoque", "ano": 2020, "km": 22000, "lkm": 8, "categoria": "luxo", "imagem": "evoque.jpg"},
    {"modelo": "Maserati Ghibli", "ano": 2023, "km": 5000, "lkm": 6, "categoria": "luxo", "imagem": "maserati.jpg"}
]

# Copiar imagens para pasta static/imagens
if not os.path.exists("../static/imagens"):
    os.makedirs("../static/imagens")

for carro in carros:
    imagem_origem = f"imagens_iniciais/{carro['imagem']}"
    imagem_destino = f"static/imagens/{carro['imagem']}"
    if os.path.exists(imagem_origem):
        shutil.copy(imagem_origem, imagem_destino)

    cursor.execute("""
        INSERT INTO carros (usuario_id, modelo, ano, km, lkm, categoria, imagem)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, carro["modelo"], carro["ano"], carro["km"], carro["lkm"], carro["categoria"], carro["imagem"]))

conn.commit()
conn.close()
print("Carros adicionados com sucesso!")

