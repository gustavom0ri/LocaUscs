from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os
import logging
import re
from send_email import email_negociacao_recebida, email_negociacao_criada, email_status_alterado
from werkzeug.utils import secure_filename
from corrigir_imagens import corrigir_caminhos_imagens

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        status TEXT DEFAULT 'Pendente',
        FOREIGN KEY (carro_id) REFERENCES carros(id)
    )''')

    conn.commit()
    conn.close()

inicializar_banco()


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

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM carros WHERE categoria = 'popular'")
    carros_populares = cursor.fetchall()

    cursor.execute("SELECT * FROM carros WHERE categoria = 'luxo'")
    carros_luxo = cursor.fetchall()

    cursor.execute("SELECT * FROM carros WHERE usuario_id = ?", (user_id,))
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
        senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()

        conn = sqlite3.connect('locauscs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE email = ? AND senha = ?', (email, senha_criptografada))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session['user_id'] = usuario[0]
            return redirect(url_for('home'))
        else:
            flash("Usuário ou senha inválidos", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        if not nome or not email or not senha:
            flash("Por favor, preencha todos os campos.", "error")
            return redirect(url_for('register_user'))

        senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()

        conn = sqlite3.connect('locauscs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
        if cursor.fetchone():
            flash("E-mail já cadastrado.", "error")
            conn.close()
            return redirect(url_for('register_user'))

        cursor.execute('INSERT INTO usuarios (username, email, senha) VALUES (?, ?, ?)', (nome, email, senha_criptografada))
        conn.commit()
        conn.close()

        flash("Usuário registrado com sucesso!", "success")
        return redirect(url_for('login'))

    return render_template('register_user.html')


def obter_email_dono_carro(id_carro):
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.email FROM usuarios u
        JOIN carros c ON c.usuario_id = u.id
        WHERE c.id = ?
    """, (id_carro,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    return None




@app.route('/registrar_carro', methods=['GET', 'POST'])
def registrar_carro():
    # Verifica se o usuário está logado
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Coleta os dados do formulário
        modelo = request.form.get('modelo')
        ano = request.form.get('ano')
        km = request.form.get('km')         # Quilometragem total
        lkm = request.form.get('lkm')       # Litros por km
        categoria = request.form.get('categoria')
        imagem_file = request.files.get('imagem')
        usuario_id = session['user_id']

        # Caminho da imagem
        caminho_imagem = None
        if imagem_file and imagem_file.filename != '':
            filename = secure_filename(imagem_file.filename)
            pasta_imagens = os.path.join('static', 'imagens')
            os.makedirs(pasta_imagens, exist_ok=True)  # Garante que a pasta existe
            caminho_imagem = os.path.join(pasta_imagens, filename)
            imagem_file.save(caminho_imagem)

        try:
            # Inserção no banco de dados
            conn = sqlite3.connect('locauscs.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO carros (modelo, ano, km, lkm, categoria, imagem, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (modelo, ano, km, lkm, categoria, caminho_imagem, usuario_id)
            )
            conn.commit()
            corrigir_caminhos_imagens()

        except Exception as e:
            print("Erro ao registrar carro:", e)
        finally:
            conn.close()

        return redirect(url_for('meus_carros'))

    # Caso seja um GET
    return render_template('registrar_carro.html')

@app.route('/meus_carros')
def meus_carros():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carros WHERE usuario_id = ?", (user_id,))
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

@app.route('/negociar/<int:id_carro>', methods=['POST'])
def negociar(id_carro):
    nome = request.form['nome']
    duracao = request.form['duracao_aluguel']
    local = request.form['local_moradia']
    valor = request.form['valor_proposto']
    email = request.form['email']
    telefone = request.form['telefone']
    whatsapp = request.form['whatsapp']
    mensagem = request.form['mensagem']

    descricao = f'''
    Nome: {nome}
    Duração do Aluguel: {duracao}
    Local de Moradia: {local}
    Valor Proposto: {valor}
    WhatsApp: {whatsapp}
    Mensagem: {mensagem}
    '''.strip()

    # Pegar o modelo do carro para colocar no e-mail
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT modelo FROM carros WHERE id = ?', (id_carro,))
    carro = cursor.fetchone()
    modelo_carro = carro[0] if carro else 'Desconhecido'

    # Inserir negociação no banco
    cursor.execute('''
        INSERT INTO negociacoes (carro_id, descricao, email_contato, telefone)
        VALUES (?, ?, ?, ?)
    ''', (id_carro, descricao, email, telefone))
    conn.commit()
    conn.close()

    # Dados para o e-mail
    dados_email = {
        'nome': nome,
        'email': email,
        'telefone': telefone,
        'whatsapp': whatsapp,
        'mensagem': mensagem,
        'valor_proposto': valor,
        'duracao': duracao,
        'local': local,
        'veiculo': modelo_carro
    }

    # Enviar e-mail ao dono do carro
    email_negociacao_recebida(id_carro, dados_email)

    # Enviar e-mail de confirmação ao locatário
    email_negociacao_criada(email, dados_email)

    flash("Negociação enviada com sucesso!", "success")
    return redirect(url_for('home', sucesso=1))



@app.route('/negociacoes', methods=['GET', 'POST'])
def negociacoes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        negociacao_id = request.form.get('negociacao_id')
        novo_status = request.form.get('status')

        # Atualizar status da negociação
        cursor.execute('UPDATE negociacoes SET status = ? WHERE id = ?', (novo_status, negociacao_id))
        conn.commit()

        # Buscar dados para email
        cursor.execute('''SELECT n.id, n.status, u.email, c.modelo
                          FROM negociacoes n
                          JOIN usuarios u ON u.email = n.email_contato
                          JOIN carros c ON c.id = n.carro_id
                          WHERE n.id = ?''', (negociacao_id,))
        resultado = cursor.fetchone()

        if resultado:
            _, status, email_locatario, modelo_veiculo = resultado
            dados_negociacao = {
                'veiculo': modelo_veiculo,
                'status': status
            }
            # Enviar email ao locatário informando a alteração de status
            email_status_alterado(email_locatario, dados_negociacao)

        flash("Status da negociação atualizado.", "success")

    # Exibir negociações relacionadas ao usuário (se dono do carro ou locatário)
    # Buscando negociações de carros que o usuário possui
    cursor.execute('''
        SELECT n.id, c.modelo, n.descricao, n.email_contato, n.telefone, n.status
        FROM negociacoes n
        JOIN carros c ON n.carro_id = c.id
        WHERE c.usuario_id = ?
    ''', (user_id,))
    negociacoes_dono = cursor.fetchall()

    # Buscando negociações feitas pelo usuário (email do locatário)
    cursor.execute('''
        SELECT n.id, c.modelo, n.descricao, n.email_contato, n.telefone, n.status
        FROM negociacoes n
        JOIN carros c ON n.carro_id = c.id
        WHERE n.email_contato = (SELECT email FROM usuarios WHERE id = ?)
    ''', (user_id,))
    negociacoes_locatario = cursor.fetchall()

    conn.close()

    return render_template('negociacoes.html',
                           negociacoes_dono=negociacoes_dono,
                           negociacoes_locatario=negociacoes_locatario)


@app.route('/recusar_negociacao', methods=['POST'])
def recusar_negociacao():
    try:
        negociacao_id = request.form.get('negociacao_id')

        if not negociacao_id:
            flash("ID da negociação não fornecido.", "error")
            return redirect(url_for('negociacoes'))

        # Certifique-se de que é um número inteiro
        try:
            negociacao_id = int(negociacao_id)
        except ValueError:
            flash("ID inválido.", "error")
            return redirect(url_for('negociacoes'))

        # Conexão e exclusão
        conn = sqlite3.connect('locauscs.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM negociacoes WHERE id = ?", (negociacao_id,))
        conn.commit()
        conn.close()

        flash("Negociação recusada com sucesso.", "success")

    except Exception as e:
        flash(f"Ocorreu um erro: {str(e)}", "error")

    return redirect(url_for('negociacoes'))

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
    senha = request.form.get('senha', '').strip()

    conn = sqlite3.connect('locauscs.db')
    cursor = conn.cursor()

    if senha:
        senha_criptografada = hashlib.sha256(senha.encode()).hexdigest()
        cursor.execute("UPDATE usuarios SET username = ?, email = ?, senha = ? WHERE id = ?",
                       (username, email, senha_criptografada, user_id))
    else:
        cursor.execute("UPDATE usuarios SET username = ?, email = ? WHERE id = ?",
                       (username, email, user_id))

    conn.commit()
    conn.close()

    flash("Perfil atualizado com sucesso!", "success")
    return redirect(url_for('perfil'))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
