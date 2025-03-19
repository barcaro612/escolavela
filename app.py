# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 15:19:27 2025

@author: Inspetor
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Permite requisições de outros domínios (frontend)

# Rota raiz
@app.route('/')
def index():
    return "Bem-vindo à API da Escola de Vela!"

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('curso_vela.db')
    conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
    return conn

# Rota para cadastrar usuário
@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    dados = request.json  # Recebe os dados do frontend
    nome_completo = dados['nome_completo']
    endereco = dados['endereco']
    telefone = dados['telefone']
    cpf = dados['cpf']
    idade = dados['idade']
    peso = dados['peso']
    usuario = dados['usuario']
    senha = dados['senha']
    tipo = dados['tipo']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO usuarios (nome_completo, endereco, telefone, cpf, idade, peso, usuario, senha, tipo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome_completo, endereco, telefone, cpf, idade, peso, usuario, senha, tipo))
        conn.commit()
        return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Usuário ou CPF já cadastrado."}), 400
    finally:
        conn.close()

# Rota para fazer login
@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    usuario = dados['usuario']
    senha = dados['senha']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"mensagem": "Login bem-sucedido!", "usuario": dict(user)}), 200
    else:
        return jsonify({"erro": "Usuário ou senha incorretos."}), 401

# Rota para agendar aula
@app.route('/agendar', methods=['POST'])
def agendar_aula():
    dados = request.json
    usuario_id = dados['usuario_id']
    data = dados['data']
    periodo = dados['periodo']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO agendamentos (usuario_id, data, periodo)
        VALUES (?, ?, ?)
    ''', (usuario_id, data, periodo))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Aula agendada com sucesso!"}), 201

# Rota para ver aulas agendadas
@app.route('/aulas/<int:usuario_id>', methods=['GET'])
def ver_aulas(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, data, periodo FROM agendamentos WHERE usuario_id = ?', (usuario_id,))
    aulas = cursor.fetchall()
    conn.close()

    return jsonify([dict(aula) for aula in aulas]), 200

# Rota para ver todos os agendamentos (instrutor)
@app.route('/agendamentos', methods=['GET'])
def ver_todos_agendamentos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT agendamentos.id, usuarios.nome_completo, agendamentos.data, agendamentos.periodo
        FROM agendamentos
        JOIN usuarios ON agendamentos.usuario_id = usuarios.id
    ''')
    agendamentos = cursor.fetchall()
    conn.close()

    return jsonify([dict(ag) for ag in agendamentos]), 200

# Rota para deletar agendamento
@app.route('/agendamentos/<int:agendamento_id>', methods=['DELETE'])
def deletar_agendamento(agendamento_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM agendamentos WHERE id = ?', (agendamento_id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Agendamento deletado com sucesso!"}), 200

# Rota para enviar mensagem
@app.route('/mensagens', methods=['POST'])
def enviar_mensagem():
    dados = request.json
    remetente_id = dados['remetente_id']
    destinatario_id = dados['destinatario_id']
    mensagem = dados['mensagem']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mensagens (remetente_id, destinatario_id, mensagem)
        VALUES (?, ?, ?)
    ''', (remetente_id, destinatario_id, mensagem))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Mensagem enviada com sucesso!"}), 201

# Rota para ver mensagens
@app.route('/mensagens/<int:destinatario_id>', methods=['GET'])
def ver_mensagens(destinatario_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mensagens.id, usuarios.usuario, mensagens.mensagem
        FROM mensagens
        JOIN usuarios ON mensagens.remetente_id = usuarios.id
        WHERE destinatario_id = ?
    ''', (destinatario_id,))
    mensagens = cursor.fetchall()
    conn.close()

    return jsonify([dict(msg) for msg in mensagens]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
