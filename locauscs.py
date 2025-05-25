from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os
import logging
from send_email import enviar_email
from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Chave secreta para sessão

# Inicialização do banco de dados
def inicializar_banco():
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS carros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        ano INTEGER NOT NULL,
        km INTEGER NOT NULL,
        lkm REAL NOT NULL,
        categoria TEXT NOT NULL,
        imagem TEXT NOT NULL,
        usuario_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS negociacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        carro_id INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        email_contato TEXT NOT NULL,
        telefone TEXT NOT NULL,
        FOREIGN KEY (carro_id) REFERENCES carros(id)
    )''')

    conn.commit()
    conn.close()

inicializar_banco()

# --- ROTAS ---

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    # Selecionar explicitamente as colunas para evitar confusão no índice
    cursor.execute("SELECT id, modelo, ano, km, lkm, categoria, imagem, usuario_id FROM carros WHERE categoria = 'popular'")
    carros_populares = cursor.fetchall()

    cursor.execute("SELECT id, modelo, ano, km, lkm, categoria, imagem, usuario_id FROM carros WHERE categoria = 'luxo'")
    carros_luxo = cursor.fetchall()

    cursor.execute("SELECT id, modelo, ano, km, lkm, categoria, imagem, usuario_id FROM carros WHERE usuario_id = ?", (user_id,))
    meus_carros = cursor.fetchall()

    conn.close()

    return render_template('home.html',
                           carros_populares=carros_populares,
                           carros_luxo=carros_luxo,
                           meus_carros=meus_carros)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        logging.debug(f"Tentativa de login com: {email}")

        # Criptografar a senha
        senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()

        # Verificar usuário no banco de dados
        conn = sqlite3.connect('locauscs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE email = ? AND senha = ?', (email, senha_criptografada))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session['user_id'] = usuario[0]
            logging.info(f"Login bem-sucedido para {email}")
            return redirect(url_for('home'))
        else:
            logging.warning("Usuário ou senha inválidos")
            flash("Usuário ou senha inválidos")  # Passa a mensagem para o template
            return redirect(url_for('login'))    # Redireciona para GET da rota, que renderiza o template
    return render_template('login.html')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        # Validação básica de campos obrigatórios
        if not nome or not email or not senha:
            flash("Por favor, preencha todos os campos.", "error")
            return redirect(url_for('register_user'))

        senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()

        conn = sqlite3.connect('locauscs.db')
        cursor = conn.cursor()

        # Verifica se o email já existe
        cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
        if cursor.fetchone():
            flash("E-mail já cadastrado. Use outro e-mail.", "error")
            conn.close()
            return redirect(url_for('register_user'))

        cursor.execute('INSERT INTO usuarios (username, email, senha) VALUES (?, ?, ?)', (nome, email, senha_criptografada))
        conn.commit()
        conn.close()

        flash("Usuário registrado com sucesso! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('register_user.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/negociar/<int:carro_id>', methods=['POST'])
def negociar(carro_id):
    descricao = request.form.get('descricao')
    email_contato = request.form.get('email')
    telefone = request.form.get('telefone')

    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    cursor.execute('SELECT modelo, usuario_id FROM carros WHERE id = ?', (carro_id,))
    carro = cursor.fetchone()
    if not carro:
        conn.close()
        return "Carro não encontrado", 404

    modelo, usuario_id = carro
    cursor.execute('SELECT email FROM usuarios WHERE id = ?', (usuario_id,))
    dono = cursor.fetchone()

    cursor.execute('''INSERT INTO negociacoes (carro_id, descricao, email_contato, telefone)
                      VALUES (?, ?, ?, ?)''', (carro_id, descricao, email_contato, telefone))
    conn.commit()
    conn.close()

    if dono:
        email_dono = dono[0]
        mensagem = f"""Subject: Aviso! Alguém está interessado em alugar o seu veículo {modelo}

Olá,

Um interessado deixou a seguinte mensagem sobre o seu carro {modelo}:

{descricao}

Informações de contato:
E-mail: {email_contato}
Telefone: {telefone}
"""
        enviar_email(mensagem)

    return redirect(url_for('home'))

@app.route('/meus_carros')
def meus_carros():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, modelo, ano, km, lkm, categoria, imagem, usuario_id FROM carros WHERE usuario_id = ?", (user_id,))
    carros = cursor.fetchall()
    conn.close()

    return render_template('meus_carros.html', carros=carros)



@app.route('/editar_carro/<int:carro_id>', methods=['POST'])
def editar_carro(carro_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    modelo = request.form['modelo']
    ano = request.form['ano']
    km = request.form['km']
    lkm = request.form['lkm']
    categoria = request.form['categoria']
    imagem = request.form['imagem']

    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE carros 
                      SET modelo = ?, ano = ?, km = ?, lkm = ?, categoria = ?, imagem = ?
                      WHERE id = ?''',
                   (modelo, ano, km, lkm, categoria, imagem, carro_id))
    conn.commit()
    conn.close()

    return redirect(url_for('meus_carros'))


@app.route('/registrar_carro', methods=['GET', 'POST'])
def registrar_carro():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        modelo = request.form['modelo']
        ano = request.form['ano']
        km = request.form['km']
        lkm = request.form['lkm']
        categoria = request.form['categoria']
        imagem = request.form['imagem']
        usuario_id = session['user_id']

        conn = sqlite3.connect('locauscs.db')
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO carros (modelo, ano, km, lkm, categoria, imagem, usuario_id) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (modelo, ano, km, lkm, categoria, imagem, usuario_id))

        conn.commit()
        conn.close()

        return redirect(url_for('meus_carros'))

    return render_template('registrar_carro.html')

@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()
    conn.close()

    return render_template('perfil.html', usuario=usuario)

@app.route('/atualizar_perfil', methods=['POST'])
def atualizar_perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = request.form['username']
    email = request.form['email']

    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET username = ?, email = ? WHERE id = ?", (username, email, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for('perfil'))

@app.route('/negociacoes')
def negociacoes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT carros.modelo, negociacoes.descricao, negociacoes.email_contato, negociacoes.telefone
                      FROM negociacoes
                      JOIN carros ON carros.id = negociacoes.carro_id
                      WHERE carros.usuario_id = ?''', (user_id,))
    negociacoes = cursor.fetchall()
    conn.close()

    return render_template('negociacoes.html', negociacoes=negociacoes)

if __name__ == '__main__':
    app.run(debug=True)
