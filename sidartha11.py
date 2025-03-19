# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 12:06:49 2025

@author: sicgu
"""
import requests
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import Calendar
import webbrowser
from tkinter import scrolledtext
from PIL import Image, ImageTk  # Importar Pillow para manipulação de imagens

# Configuração do Banco de Dados
def criar_banco_de_dados():
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nome_completo TEXT,
                  endereco TEXT,
                  telefone TEXT,
                  cpf TEXT UNIQUE,
                  idade INTEGER,
                  peso REAL,
                  usuario TEXT UNIQUE,
                  senha TEXT,
                  tipo TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS agendamentos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  usuario_id INTEGER,
                  data TEXT,
                  periodo TEXT,
                  FOREIGN KEY(usuario_id) REFERENCES usuarios(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS mensagens
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  remetente_id INTEGER,
                  destinatario_id INTEGER,
                  mensagem TEXT,
                  FOREIGN KEY(remetente_id) REFERENCES usuarios(id),
                  FOREIGN KEY(destinatario_id) REFERENCES usuarios(id))''')

    conn.commit()
    conn.close()

criar_banco_de_dados()

# Funções do Banco de Dados
def cadastrar_usuario(nome_completo, endereco, telefone, cpf, idade, peso, usuario, senha, tipo, palavra_passe=""):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    if tipo == "instrutor" and palavra_passe != "Buda":
        messagebox.showerror("Erro", "Palavra passe incorreta para instrutor.")
        return False

    try:
        c.execute(
            "INSERT INTO usuarios (nome_completo, endereco, telefone, cpf, idade, peso, usuario, senha, tipo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nome_completo, endereco, telefone, cpf, idade, peso, usuario, senha, tipo))
        conn.commit()
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Usuário ou CPF já cadastrado.")
        return False
    finally:
        conn.close()

class CadastroScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro")
        self.root.geometry("600x600")
        self.root.configure(bg="black")

        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de cadastro
        cadastro_frame = tk.Frame(main_frame, bg="black", bd=2, relief=tk.GROOVE)
        cadastro_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(cadastro_frame, text="Cadastro", bg="black", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        # Campos de entrada
        campos = [
            ("Nome Completo:", tk.Entry(cadastro_frame, font=("Helvetica", 12))),
            ("Endereço:", tk.Entry(cadastro_frame, font=("Helvetica", 12))),
            ("Telefone:", tk.Entry(cadastro_frame, font=("Helvetica", 12))),
            ("CPF:", tk.Entry(cadastro_frame, font=("Helvetica", 12))),
            ("Idade:", tk.Entry(cadastro_frame, font=("Helvetica", 12))),
            ("Peso:", tk.Entry(cadastro_frame, font=("Helvetica", 12))),
            ("Usuário:", tk.Entry(cadastro_frame, font=("Helvetica", 12))),
            ("Senha:", tk.Entry(cadastro_frame, show="*", font=("Helvetica", 12))),
            ("Confirmar Senha:", tk.Entry(cadastro_frame, show="*", font=("Helvetica", 12))),
        ]

        # Adicionar rótulos e campos ao frame
        for i, (label_text, entry) in enumerate(campos):
            row = (i // 3) * 2 + 1
            col = i % 3
            tk.Label(cadastro_frame, text=label_text, bg="black", fg="white").grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry.grid(row=row + 1, column=col, padx=10, pady=5, sticky="ew")

        # Armazenar campos em uma lista para acesso fácil
        self.campos = [entry for _, entry in campos]

        # Radiobuttons para "aluno" e "instrutor"
        self.tipo_var = tk.StringVar(value="aluno")
        tk.Label(cadastro_frame, text="Tipo:", bg="black", fg="white").grid(row=len(campos) * 2 + 1, column=0, padx=10, pady=5, sticky="w")
        tk.Radiobutton(
            cadastro_frame, text="Aluno", variable=self.tipo_var, value="aluno",
            bg="black", fg="white", selectcolor="gray"  # Cor do indicador de seleção
        ).grid(row=len(campos) * 2 + 2, column=0, padx=10, pady=5, sticky="w")
        tk.Radiobutton(
            cadastro_frame, text="Instrutor", variable=self.tipo_var, value="instrutor",
            bg="black", fg="white", selectcolor="gray"  # Cor do indicador de seleção
        ).grid(row=len(campos) * 2 + 2, column=1, padx=10, pady=5, sticky="w")

        # Botões
        botoes_frame = tk.Frame(cadastro_frame, bg="black")
        botoes_frame.grid(row=(len(campos) // 3) * 2 + 4, column=0, columnspan=3, pady=20)
        tk.Button(botoes_frame, text="Visualizar Dados", command=self.visualizar_dados).grid(row=0, column=0, padx=10)
        tk.Button(botoes_frame, text="Cadastrar", command=self.cadastrar).grid(row=0, column=1, padx=10)

    def visualizar_dados(self):
        dados = {
            "Nome Completo": self.campos[0].get(),
            "Endereço": self.campos[1].get(),
            "Telefone": self.campos[2].get(),
            "CPF": self.campos[3].get(),
            "Idade": self.campos[4].get(),
            "Peso": self.campos[5].get(),
            "Usuário": self.campos[6].get(),
            "Senha": self.campos[7].get(),
            "Confirmar Senha": self.campos[8].get(),
            "Tipo": self.tipo_var.get(),
        }

        # Exibir dados em uma nova janela
        dados_window = tk.Toplevel(self.root)
        dados_window.title("Dados Digitados")
        dados_window.geometry("400x300")
        dados_window.configure(bg="black")

        tk.Label(dados_window, text="\n".join(f"{k}: {v}" for k, v in dados.items()), bg="black", fg="white").pack(padx=10, pady=10)

    def cadastrar(self):
        # Coletar dados
        dados = [entry.get() for entry in self.campos]
        tipo = self.tipo_var.get()

        # Verificar se as senhas coincidem
        if dados[7] != dados[8]:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return

        # Verificar palavra-passe para instrutor
        if tipo == "instrutor":
            palavra_passe = simpledialog.askstring("Palavra Passe", "Digite a palavra passe para instrutor:")
            if palavra_passe is None or palavra_passe.strip().lower() != "buda":
                messagebox.showerror("Erro", "Palavra passe incorreta para instrutor.")
                return

        # Cadastrar usuário
        if self.cadastrar_usuario(*dados[:8], tipo):
            self.root.destroy()

    def cadastrar_usuario(self, nome_completo, endereco, telefone, cpf, idade, peso, usuario, senha, tipo):
        conn = sqlite3.connect('curso_vela.db')
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO usuarios (nome_completo, endereco, telefone, cpf, idade, peso, usuario, senha, tipo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (nome_completo, endereco, telefone, cpf, idade, peso, usuario, senha, tipo))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário ou CPF já cadastrado.")
            return False
        finally:
            conn.close()

class AlunoScreen:
    def __init__(self, root, usuario_id):
        self.root = root
        self.usuario_id = usuario_id
        self.root.title("Aluno")
        self.root.geometry("600x500")
        self.root.configure(bg="black")  # Fundo preto para a janela principal

        # Configurar estilo para fundo preto e texto branco
        style = ttk.Style()
        style.configure("Black.TFrame", background="black")
        style.configure("Black.TLabel", background="black", foreground="white")
        style.configure("Black.TButton", background="white", foreground="black",
                        font=("Helvetica", 12))  # Texto preto
        style.map("Black.TButton", background=[("active", "gray")])  # Cor ao passar o mouse

        # Frame principal com fundo preto
        main_frame = ttk.Frame(root, padding="20", style="Black.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Centralizar conteúdo
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)

        # Moldura para os botões (usando tk.Frame em vez de ttk.LabelFrame)
        botoes_frame = tk.Frame(main_frame, bg="black", bd=2, relief=tk.GROOVE)
        botoes_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Título da moldura
        titulo_frame = tk.Label(botoes_frame, text="Menu do Aluno", bg="black", fg="white",
                                font=("Helvetica", 12, "bold"))
        titulo_frame.pack(pady=10)

        # Botões com texto preto
        ttk.Button(botoes_frame, text="Agendar Aula", command=self.abrir_calendario, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Enviar Agendamentos ao Instrutor", command=self.enviar_agendamentos,
                   style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Ver Aulas Agendadas", command=self.ver_aulas, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Ver Mensagens", command=self.ver_mensagens, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Ver Previsão do Tempo", command=self.abrir_windy, style="Black.TButton").pack(pady=10)

        # Rótulo de atenção abaixo do último botão
        rotulo_atencao = tk.Label(
            botoes_frame,
            text="Atenção!! Não esqueça de enviar seus agendamentos ao Instrutor, após escolher todos os dias clique em 'Enviar agendamentos ao Instrutor'.",
            font=("Comic Sans MS", 16),
            fg="red",  # Cor do texto
            bg="black",  # Cor de fundo
            wraplength=500  # Define a largura máxima antes de quebrar a linha
        )
        rotulo_atencao.pack(pady=20)  # Adiciona espaço vertical após o rótulo

        # Adicionar rótulo fixo no canto inferior direito
        footer_label = ttk.Label(main_frame,
                                 text="Veleaulas\n1.0\n© 2025 Edson Barcaro - Todos os direitos reservados.",
                                 style="Black.TLabel", justify="right")
        footer_label.grid(row=4, column=1, sticky="se", padx=10, pady=10)

    def on_close(self):
        # Exibe uma caixa de diálogo perguntando se o aluno enviou os agendamentos
        resposta = messagebox.askyesno("Confirmação", "Você enviou os agendamentos para o Instrutor?")

        if resposta:  # Se o aluno respondeu "Sim"
            self.root.destroy()  # Fecha a janela
        else:
            # Se o aluno respondeu "Não", a janela não é fechada
            messagebox.showinfo("Informação", "Por favor, envie os agendamentos antes de sair.")

    def abrir_calendario(self):
        calendario_window = tk.Toplevel(self.root)
        calendario_window.title("Escolha a Data")
        calendario_window.configure(bg="black")  # Fundo preto para a janela

        calendario = Calendar(calendario_window, selectmode="day")
        calendario.pack(padx=20, pady=20)

        tk.Label(calendario_window, text="Período:", bg="black", fg="white").pack()
        periodo_var = tk.StringVar(value="Manhã")
        tk.Radiobutton(calendario_window, text="Manhã", variable=periodo_var, value="Manhã", bg="black",
                       fg="white", selectcolor="black").pack()  # Adiciona selectcolor
        tk.Radiobutton(calendario_window, text="Tarde", variable=periodo_var, value="Tarde", bg="black",
                       fg="white", selectcolor="black").pack()  # Adiciona selectcolor
        tk.Radiobutton(calendario_window, text="Integral", variable=periodo_var, value="Integral", bg="black",
                       fg="white", selectcolor="black").pack()  # Adiciona selectcolor

        ttk.Button(calendario_window, text="Agendar",
                   command=lambda: self.agendar(calendario.get_date(), periodo_var.get()),
                   style="Black.TButton").pack(pady=10)

    def agendar(self, data, periodo):
        agendar_aula(self.usuario_id, data, periodo)
        messagebox.showinfo("Sucesso", "Aula agendada com sucesso!")

    def enviar_agendamentos(self):
        # Lógica para enviar agendamentos ao instrutor
        messagebox.showinfo("Sucesso", "Agendamentos enviados ao instrutor com sucesso!")

    def ver_aulas(self):
        aulas = ver_aulas_agendadas(self.usuario_id)
        if aulas:
            # Criar uma nova janela para exibir as aulas agendadas
            aulas_window = tk.Toplevel(self.root)
            aulas_window.title("Aulas Agendadas")
            aulas_window.geometry("600x400")
            aulas_window.configure(bg="black")  # Fundo preto para a janela

            # Frame interno com fundo preto
            aulas_frame = ttk.Frame(aulas_window, padding="20", style="Black.TFrame")
            aulas_frame.pack(fill=tk.BOTH, expand=True)

            # Criar um ScrolledText para exibir o conteúdo
            scroll_text = scrolledtext.ScrolledText(aulas_frame, wrap=tk.WORD, width=70, height=20,
                                                    font=("Helvetica", 12), bg="black", fg="white")
            scroll_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Preencher o ScrolledText com as aulas agendadas
            for aula in aulas:
                scroll_text.insert(tk.END, f"Data: {aula[1]}, Período: {aula[2]}\n\n")

            # Desabilitar a edição do texto (apenas leitura)
            scroll_text.configure(state=tk.DISABLED)
        else:
            messagebox.showinfo("Aulas Agendadas", "Nenhuma aula agendada.")

    def ver_mensagens(self):
        mensagens = ver_mensagens(self.usuario_id)
        if mensagens:
            # Criar uma nova janela para exibir as mensagens
            mensagens_window = tk.Toplevel(self.root)
            mensagens_window.title("Mensagens")
            mensagens_window.geometry("600x400")
            mensagens_window.configure(bg="black")  # Fundo preto para a janela

            # Frame interno com fundo preto
            mensagens_frame = ttk.Frame(mensagens_window, padding="20", style="Black.TFrame")
            mensagens_frame.pack(fill=tk.BOTH, expand=True)

            # Criar um ScrolledText para exibir o conteúdo
            scroll_text = scrolledtext.ScrolledText(mensagens_frame, wrap=tk.WORD, width=70, height=20,
                                                    font=("Helvetica", 12), bg="black", fg="white")
            scroll_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Preencher o ScrolledText com as mensagens
            for msg in mensagens:
                scroll_text.insert(tk.END, f"De: {msg[1]}, Mensagem: {msg[2]}\n\n")

            # Desabilitar a edição do texto (apenas leitura)
            scroll_text.configure(state=tk.DISABLED)

            # Manter a janela em foco
            mensagens_window.grab_set()

            # Perguntar se deseja deletar as mensagens após a leitura
            deletar = messagebox.askyesno("Mensagens", "Deseja deletar as mensagens após a leitura?")
            if deletar:
                for msg in mensagens:
                    deletar_mensagem(msg[0])
                messagebox.showinfo("Sucesso", "Mensagens deletadas com sucesso!")
        else:
            messagebox.showinfo("Mensagens", "Nenhuma mensagem.")

    def abrir_windy(self):
        webbrowser.open("https://www.windy.com/-22.733/-46.358?piracaia")


def login(usuario, senha):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    user = c.fetchone()

    conn.close()
    return user

def agendar_aula(usuario_id, data, periodo):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("INSERT INTO agendamentos (usuario_id, data, periodo) VALUES (?, ?, ?)",
              (usuario_id, data, periodo))
    conn.commit()
    conn.close()

def ver_aulas_agendadas(usuario_id):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("SELECT id, data, periodo FROM agendamentos WHERE usuario_id = ?", (usuario_id,))
    aulas = c.fetchall()

    conn.close()
    return aulas

def ver_todos_agendamentos():
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute(
        "SELECT agendamentos.id, usuarios.nome_completo, agendamentos.data, agendamentos.periodo FROM agendamentos JOIN usuarios ON agendamentos.usuario_id = usuarios.id")
    agendamentos = c.fetchall()

    conn.close()
    return agendamentos

def deletar_agendamento(agendamento_id):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
    conn.commit()
    conn.close()

def deletar_todos_agendamentos():
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("DELETE FROM agendamentos")
    conn.commit()
    conn.close()

def editar_agendamento(agendamento_id, nova_data, novo_periodo):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("UPDATE agendamentos SET data = ?, periodo = ? WHERE id = ?", (nova_data, novo_periodo, agendamento_id))
    conn.commit()
    conn.close()

def ver_usuarios_cadastrados():
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("SELECT id, nome_completo, endereco, telefone, cpf, idade, peso, usuario, tipo FROM usuarios")
    usuarios = c.fetchall()

    conn.close()
    return usuarios

def ver_detalhes_usuario(usuario_id):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = c.fetchone()

    conn.close()
    return usuario

def deletar_usuario(usuario_id):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()


def formar_turmas():
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("""
        SELECT agendamentos.data, agendamentos.periodo, usuarios.nome_completo, usuarios.peso 
        FROM agendamentos 
        JOIN usuarios ON agendamentos.usuario_id = usuarios.id 
        ORDER BY agendamentos.data, agendamentos.periodo
    """)
    turmas = c.fetchall()

    conn.close()

    # Agrupar por data e período
    turmas_agrupadas = {}
    for data, periodo, nome, peso in turmas:
        if data and periodo and nome and peso:  # Verificar se os dados não estão vazios
            if data not in turmas_agrupadas:
                turmas_agrupadas[data] = {}
            if periodo not in turmas_agrupadas[data]:
                turmas_agrupadas[data][periodo] = []
            turmas_agrupadas[data][periodo].append((nome, peso))

    return turmas_agrupadas

def enviar_mensagem(remetente_id, destinatario_id, mensagem):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("INSERT INTO mensagens (remetente_id, destinatario_id, mensagem) VALUES (?, ?, ?)",
              (remetente_id, destinatario_id, mensagem))
    conn.commit()
    conn.close()

def ver_mensagens(destinatario_id):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("""
        SELECT mensagens.id, usuarios.usuario, mensagens.mensagem 
        FROM mensagens 
        JOIN usuarios ON mensagens.remetente_id = usuarios.id 
        WHERE destinatario_id = ?
    """, (destinatario_id,))
    mensagens = c.fetchall()

    conn.close()
    return mensagens

def deletar_mensagem(mensagem_id):
    conn = sqlite3.connect('curso_vela.db')
    c = conn.cursor()

    c.execute("DELETE FROM mensagens WHERE id = ?", (mensagem_id,))
    conn.commit()
    conn.close()


class InstrutorScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Instrutor")
        self.root.geometry("800x600")
        self.root.configure(bg="black")  # Fundo preto para a janela principal

        # Configurar estilo para fundo preto e texto preto nos botões
        style = ttk.Style()
        style.configure("Black.TFrame", background="black")
        style.configure("Black.TLabel", background="black", foreground="white")
        style.configure("Black.TButton", background="white", foreground="black", font=("Helvetica", 12))  # Texto preto
        style.map("Black.TButton", background=[("active", "gray")])  # Cor ao passar o mouse

        # Frame principal com fundo preto
        main_frame = ttk.Frame(root, padding="20", style="Black.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Centralizar conteúdo
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_rowconfigure(5, weight=1)
        main_frame.grid_rowconfigure(6, weight=1)
        main_frame.grid_rowconfigure(7, weight=1)

        # Moldura para os botões (usando tk.Frame em vez de ttk.LabelFrame)
        botoes_frame = tk.Frame(main_frame, bg="black", bd=2, relief=tk.GROOVE)
        botoes_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Título da moldura
        titulo_frame = tk.Label(botoes_frame, text="Menu do Instrutor", bg="black", fg="white", font=("Helvetica", 12, "bold"))
        titulo_frame.pack(pady=10)

        # Botões com texto preto
        ttk.Button(botoes_frame, text="Ver Agendamentos", command=self.ver_agendamentos, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Deletar Agendamento", command=self.deletar_agendamento, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Deletar Todos os Agendamentos", command=self.deletar_todos_agendamentos, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Editar Agendamento", command=self.editar_agendamento, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Ver Usuários Cadastrados", command=self.ver_usuarios, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Formar Turmas", command=self.formar_turmas, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Enviar Mensagem", command=self.enviar_mensagem, style="Black.TButton").pack(pady=10)
        ttk.Button(botoes_frame, text="Deletar Usuário", command=self.deletar_usuario, style="Black.TButton").pack(pady=10)

    def ver_agendamentos(self):
        agendamentos = ver_todos_agendamentos()
        if agendamentos:
            # Criar uma nova janela para exibir os agendamentos
            agendamentos_window = tk.Toplevel(self.root)
            agendamentos_window.title("Agendamentos")
            agendamentos_window.geometry("600x400")
            agendamentos_window.configure(bg="black")  # Fundo preto para a janela

            # Frame interno com fundo preto
            agendamentos_frame = ttk.Frame(agendamentos_window, padding="20", style="Black.TFrame")
            agendamentos_frame.pack(fill=tk.BOTH, expand=True)

            # Criar um ScrolledText para exibir o conteúdo
            scroll_text = scrolledtext.ScrolledText(agendamentos_frame, wrap=tk.WORD, width=70, height=20, font=("Helvetica", 12), bg="black", fg="white")
            scroll_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Preencher o ScrolledText com os agendamentos
            for ag in agendamentos:
                scroll_text.insert(tk.END, f"ID: {ag[0]}, Aluno: {ag[1]}, Data: {ag[2]}, Período: {ag[3]}\n\n")

            # Desabilitar a edição do texto (apenas leitura)
            scroll_text.configure(state=tk.DISABLED)
        else:
            messagebox.showinfo("Agendamentos", "Nenhum agendamento encontrado.")

    def deletar_agendamento(self):
        # Criar uma nova janela para deletar agendamento
        deletar_window = tk.Toplevel(self.root)
        deletar_window.title("Deletar Agendamento")
        deletar_window.geometry("400x150")
        deletar_window.configure(bg="black")  # Fundo preto para a janela

        # Frame interno com fundo preto
        deletar_frame = ttk.Frame(deletar_window, padding="20", style="Black.TFrame")
        deletar_frame.pack(fill=tk.BOTH, expand=True)

        # Label e Entry para o ID do agendamento
        ttk.Label(deletar_frame, text="ID do Agendamento:", style="Black.TLabel").grid(row=0, column=0, padx=10,
                                                                                       pady=10)
        agendamento_id_entry = ttk.Entry(deletar_frame, font=("Helvetica", 12))
        agendamento_id_entry.grid(row=0, column=1, padx=10, pady=10)

        # Botão para confirmar a deleção
        def confirmar_delecao():
            agendamento_id = agendamento_id_entry.get()
            if agendamento_id:
                deletar_agendamento(int(agendamento_id))
                messagebox.showinfo("Sucesso", "Agendamento deletado com sucesso!")
                deletar_window.destroy()

        ttk.Button(deletar_frame, text="Deletar", command=confirmar_delecao, style="Black.TButton").grid(row=1,
                                                                                                         column=0,
                                                                                                         columnspan=2,
                                                                                                         pady=10)

    def deletar_todos_agendamentos(self):
        confirmacao = messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar todos os agendamentos?")
        if confirmacao:
            deletar_todos_agendamentos()
            messagebox.showinfo("Sucesso", "Todos os agendamentos foram deletados.")

    def editar_agendamento(self):
        # Criar uma nova janela para editar agendamento
        editar_window = tk.Toplevel(self.root)
        editar_window.title("Editar Agendamento")
        editar_window.geometry("400x250")
        editar_window.configure(bg="black")  # Fundo preto para a janela

        # Frame interno com fundo preto
        editar_frame = ttk.Frame(editar_window, padding="20", style="Black.TFrame")
        editar_frame.pack(fill=tk.BOTH, expand=True)

        # Label e Entry para o ID do agendamento
        ttk.Label(editar_frame, text="ID do Agendamento:", style="Black.TLabel").grid(row=0, column=0, padx=10, pady=10)
        agendamento_id_entry = ttk.Entry(editar_frame, font=("Helvetica", 12))
        agendamento_id_entry.grid(row=0, column=1, padx=10, pady=10)

        # Label e Entry para a nova data
        ttk.Label(editar_frame, text="Nova Data (YYYY-MM-DD):", style="Black.TLabel").grid(row=1, column=0, padx=10,
                                                                                           pady=10)
        nova_data_entry = ttk.Entry(editar_frame, font=("Helvetica", 12))
        nova_data_entry.grid(row=1, column=1, padx=10, pady=10)

        # Label e Entry para o novo período
        ttk.Label(editar_frame, text="Novo Período (Manhã, Tarde, Integral):", style="Black.TLabel").grid(row=2,
                                                                                                          column=0,
                                                                                                          padx=10,
                                                                                                          pady=10)
        novo_periodo_entry = ttk.Entry(editar_frame, font=("Helvetica", 12))
        novo_periodo_entry.grid(row=2, column=1, padx=10, pady=10)

        # Botão para confirmar a edição
        def confirmar_edicao():
            agendamento_id = agendamento_id_entry.get()
            nova_data = nova_data_entry.get()
            novo_periodo = novo_periodo_entry.get()
            if agendamento_id and nova_data and novo_periodo:
                editar_agendamento(int(agendamento_id), nova_data, novo_periodo)
                messagebox.showinfo("Sucesso", "Agendamento editado com sucesso!")
                editar_window.destroy()

        ttk.Button(editar_frame, text="Editar", command=confirmar_edicao, style="Black.TButton").grid(row=3, column=0,
                                                                                                      columnspan=2,
                                                                                                      pady=10)

    def ver_usuarios(self):
        usuarios = ver_usuarios_cadastrados()
        if usuarios:
            # Criar uma nova janela para exibir os usuários
            usuarios_window = tk.Toplevel(self.root)
            usuarios_window.title("Usuários Cadastrados")
            usuarios_window.geometry("600x400")
            usuarios_window.configure(bg="black")  # Fundo preto para a janela

            # Frame interno com fundo preto
            usuarios_frame = ttk.Frame(usuarios_window, padding="20", style="Black.TFrame")
            usuarios_frame.pack(fill=tk.BOTH, expand=True)

            # Criar um ScrolledText para exibir o conteúdo
            scroll_text = scrolledtext.ScrolledText(usuarios_frame, wrap=tk.WORD, width=70, height=20, font=("Helvetica", 12), bg="black", fg="white")
            scroll_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Preencher o ScrolledText com os usuários
            for usuario in usuarios:
                scroll_text.insert(tk.END, f"ID: {usuario[0]}, Nome: {usuario[1]}, Endereço: {usuario[2]}, Telefone: {usuario[3]}, CPF: {usuario[4]}, Idade: {usuario[5]}, Peso: {usuario[6]}, Usuário: {usuario[7]}, Tipo: {usuario[8]}\n\n")

            # Desabilitar a edição do texto (apenas leitura)
            scroll_text.configure(state=tk.DISABLED)
        else:
            messagebox.showinfo("Usuários Cadastrados", "Nenhum usuário cadastrado.")

    def formar_turmas(self):
        turmas_agrupadas = formar_turmas()
        if turmas_agrupadas:
            # Criar uma nova janela para exibir as turmas
            turmas_window = tk.Toplevel(self.root)
            turmas_window.title("Turmas Formadas")
            turmas_window.geometry("600x400")
            turmas_window.configure(bg="black")  # Fundo preto para a janela

            # Frame interno com fundo preto
            turmas_frame = ttk.Frame(turmas_window, padding="20", style="Black.TFrame")
            turmas_frame.pack(fill=tk.BOTH, expand=True)

            # Criar um ScrolledText para exibir o conteúdo
            scroll_text = scrolledtext.ScrolledText(turmas_frame, wrap=tk.WORD, width=70, height=20, font=("Helvetica", 12), bg="black", fg="white")
            scroll_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Preencher o ScrolledText com as turmas
            for data, periodos in turmas_agrupadas.items():
                scroll_text.insert(tk.END, f"Data: {data}\n")
                for periodo, alunos in periodos.items():
                    scroll_text.insert(tk.END, f"  Período: {periodo}\n")
                    for nome, peso in alunos:
                        scroll_text.insert(tk.END, f"    Aluno: {nome}, Peso: {peso} kg\n")
                scroll_text.insert(tk.END, "\n")  # Espaço entre as datas

            # Desabilitar a edição do texto (apenas leitura)
            scroll_text.configure(state=tk.DISABLED)
        else:
            messagebox.showinfo("Turmas Formadas", "Nenhum agendamento para formar turmas.")

    def enviar_mensagem(self):
        # Criar uma nova janela para enviar mensagem
        mensagem_window = tk.Toplevel(self.root)
        mensagem_window.title("Enviar Mensagem")
        mensagem_window.geometry("400x200")
        mensagem_window.configure(bg="black")  # Fundo preto para a janela

        # Frame interno com fundo preto
        mensagem_frame = ttk.Frame(mensagem_window, padding="20", style="Black.TFrame")
        mensagem_frame.pack(fill=tk.BOTH, expand=True)

        # Label e Entry para o ID do destinatário
        ttk.Label(mensagem_frame, text="ID do Destinatário:", style="Black.TLabel").grid(row=0, column=0, padx=10,
                                                                                         pady=10)
        destinatario_id_entry = ttk.Entry(mensagem_frame, font=("Helvetica", 12))
        destinatario_id_entry.grid(row=0, column=1, padx=10, pady=10)

        # Label e Entry para a mensagem
        ttk.Label(mensagem_frame, text="Mensagem:", style="Black.TLabel").grid(row=1, column=0, padx=10, pady=10)
        mensagem_entry = ttk.Entry(mensagem_frame, font=("Helvetica", 12))
        mensagem_entry.grid(row=1, column=1, padx=10, pady=10)

        # Botão para enviar a mensagem
        def enviar():
            destinatario_id = destinatario_id_entry.get()
            mensagem = mensagem_entry.get()
            if destinatario_id and mensagem:
                enviar_mensagem(1, int(destinatario_id), mensagem)  # Assume que o instrutor tem ID 1
                messagebox.showinfo("Sucesso", "Mensagem enviada com sucesso!")
                mensagem_window.destroy()

        ttk.Button(mensagem_frame, text="Enviar", command=enviar, style="Black.TButton").grid(row=2, column=0,
                                                                                              columnspan=2, pady=10)

    def deletar_usuario(self):
        usuario_id = simpledialog.askinteger("Deletar Usuário", "ID do Usuário:")
        if usuario_id:
            deletar_usuario(usuario_id)
            messagebox.showinfo("Sucesso", "Usuário deletado com sucesso!")

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x400")
        self.root.configure(bg="black")  # Fundo preto para a janela de login

        # Configurar estilo para fundo preto e texto preto nos botões
        style = ttk.Style()
        style.configure("Black.TFrame", background="black")
        style.configure("Black.TLabel", background="black", foreground="white")
        style.configure("Black.TButton", background="white", foreground="black", font=("Helvetica", 12))  # Texto preto
        style.map("Black.TButton", background=[("active", "gray")])  # Cor ao passar o mouse

        # Frame principal com fundo preto
        main_frame = ttk.Frame(root, padding="20", style="Black.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Centralizar conteúdo
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)

        # Adicionar logotipo
        try:
            # Atualize o caminho da imagem para o local correto no seu sistema
            self.logo_image = Image.open("C:\\Users\\Inspetor\\Desktop\\sidarthanautica\\logosidartha.png")
            self.logo_image = self.logo_image.resize((150, 150), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            logo_label = ttk.Label(main_frame, image=self.logo_photo, style="Black.TLabel")
            logo_label.grid(row=0, column=0, columnspan=2, pady=10)
        except Exception as e:
            print(f"Erro ao carregar o logotipo: {e}")
            # Se a imagem não for carregada, exiba um rótulo de texto no lugar
            logo_label = ttk.Label(main_frame, text="Logotipo não encontrado", style="Black.TLabel")
            logo_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Moldura para o formulário de login (usando tk.Frame em vez de ttk.LabelFrame)
        login_frame = tk.Frame(main_frame, bg="black", bd=2, relief=tk.GROOVE)
        login_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)

        # Título da moldura
        titulo_frame = tk.Label(login_frame, text="Login", bg="black", fg="white", font=("Helvetica", 12, "bold"))
        titulo_frame.pack(pady=10)

        ttk.Label(login_frame, text="Usuário:", style="Black.TLabel").pack(pady=10)
        self.usuario_entry = ttk.Entry(login_frame, font=("Helvetica", 12))
        self.usuario_entry.pack(pady=10)

        ttk.Label(login_frame, text="Senha:", style="Black.TLabel").pack(pady=10)
        self.senha_entry = ttk.Entry(login_frame, show="*", font=("Helvetica", 12))
        self.senha_entry.pack(pady=10)

        # Botão de login
        ttk.Button(login_frame, text="Login", command=self.login, style="Black.TButton").pack(pady=20)

        # Botão de cadastro
        ttk.Button(main_frame, text="Cadastrar", command=self.abrir_tela_cadastro, style="Black.TButton").grid(row=3, column=0, columnspan=2, pady=10)

        # Adicionar rótulo fixo no canto inferior direito
        footer_label = ttk.Label(main_frame, text="Veleaulas\n1.0\n© 2025 Edson Barcaro - Todos os direitos reservados.",
                                 style="Black.TLabel", justify="right")
        footer_label.grid(row=4, column=1, sticky="se", padx=10, pady=10)

    def login(self):
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()

        # Verificar se os campos estão preenchidos
        if not usuario or not senha:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        # Aqui você pode adicionar a lógica de login
        # Exemplo: Verificar no banco de dados
        conn = sqlite3.connect('curso_vela.db')
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        user = c.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Sucesso", "Login bem-sucedido!")
            self.root.destroy()  # Fecha a tela de login
            if user[9] == "aluno":  # Verifica o tipo de usuário
                root = tk.Tk()
                AlunoScreen(root, user[0])  # Abre a tela do aluno
                root.mainloop()
            elif user[9] == "instrutor":
                root = tk.Tk()
                InstrutorScreen(root)  # Abre a tela do instrutor
                root.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def abrir_tela_cadastro(self):
        cadastro_window = tk.Toplevel(self.root)
        CadastroScreen(cadastro_window)



# Inicialização do Programa
if __name__ == "__main__":
    root = tk.Tk()
    LoginScreen(root)
    root.mainloop()

