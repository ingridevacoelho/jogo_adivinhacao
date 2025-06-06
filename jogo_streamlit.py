import streamlit as st
import random
import sqlite3
import time
from PIL import Image
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Jogo de Adivinhação",
    page_icon="🎯",
    layout="wide"
)

# Estilo personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #FF4B4B;
        text-align: center;
    }
    .subheader {
        font-size: 1.5rem;
        color: #0068C9;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .heart-container {
        font-size: 2rem;
        color: #FF4B4B;
    }
    .instructions {
        background-color: #e6f3ff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .game-over {
        color: #FF4B4B;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Criar pasta data se não existir
os.makedirs('data', exist_ok=True)

# Função para conectar ao banco de dados
@st.cache_resource
def get_connection():
    return sqlite3.connect('data/ranking.db', check_same_thread=False)

# Inicializar banco de dados
def init_db():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ranking (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT,
                     tentativas INTEGER,
                     tempo REAL,
                     nivel TEXT,
                     data TIMESTAMP,
                     vidas_restantes INTEGER)''')
        conn.commit()
    except Exception as e:
        st.error(f"Erro ao inicializar banco de dados: {e}")

# Função para salvar vencedor no banco de dados
def salvar_vencedor(nome, tentativas, tempo_total, nivel, vidas_restantes):
    try:
        conn = get_connection()
        c = conn.cursor()
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO ranking (nome, tentativas, tempo, nivel, data, vidas_restantes) VALUES (?, ?, ?, ?, ?, ?)",
                  (nome, tentativas, tempo_total, nivel, data_atual, vidas_restantes))
        conn.commit()
    except Exception as e:
        st.error(f"Erro ao salvar vencedor: {e}")

# Função para mostrar ranking por nível usando pandas
def mostrar_ranking():
    try:
        conn = get_connection()
        st.sidebar.markdown("<h2 style='text-align: center;'>🏆 Ranking de Vencedores</h2>", unsafe_allow_html=True)
        
        niveis = ['Fácil', 'Médio', 'Difícil']
        nivel_selecionado = st.sidebar.selectbox("Filtrar por nível:", ["Todos"] + niveis)
        
        if nivel_selecionado == "Todos":
            query = "SELECT nome, tentativas, tempo, nivel, vidas_restantes, data FROM ranking ORDER BY tentativas ASC, tempo ASC LIMIT 10"
            df = pd.read_sql_query(query, conn)
        else:
            query = "SELECT nome, tentativas, tempo, nivel, vidas_restantes, data FROM ranking WHERE nivel = ? ORDER BY tentativas ASC, tempo ASC LIMIT 10"
            df = pd.read_sql_query(query, conn, params=(nivel_selecionado,))
        
        if not df.empty:
            df.columns = ['Nome', 'Tentativas', 'Tempo (s)', 'Nível', 'Vidas', 'Data']
            df['Tempo (s)'] = df['Tempo (s)'].round(2)
            df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d/%m/%Y %H:%M')
            df.index = df.index + 1  # Começar do índice 1
            st.sidebar.dataframe(df, use_container_width=True)
        else:
            st.sidebar.info("Nenhum vencedor registrado ainda.")
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar ranking: {e}")

# Função para gerar dicas baseadas no palpite
def gerar_dica(palpite, numero_secreto, nivel):
    diferenca = abs(palpite - numero_secreto)
    limite = {"Fácil": 50, "Médio": 100, "Difícil": 200}
    
    if nivel == "Fácil":
        if diferenca <= 5:
            return "🔥 Muito quente! Você está muito perto!"
        elif diferenca <= 10:
            return "😊 Quente! Está se aproximando!"
        else:
            return "❄️ Frio! Tente novamente."
    elif nivel == "Médio":
        if diferenca <= 10:
            return "🔥 Quente! Está se aproximando!"
        else:
            return "❄️ Frio! Tente novamente."
    else:  # Difícil
        if diferenca <= 20:
            return "🔥 Quente! Está se aproximando!"
        else:
            return "❄️ Frio! Tente novamente."

# Função para exibir vidas
def exibir_vidas(vidas, vidas_iniciais):
    return "❤️" * vidas + "🖤" * (vidas_iniciais - vidas)

# Função para exibir histórico de palpites
def mostrar_historico_palpites(palpites, numero_secreto):
    """Mostra o histórico de palpites do jogador"""
    if palpites:
        st.write("### Seus palpites anteriores:")
        for i, p in enumerate(palpites, 1):
            if p < numero_secreto:
                st.write(f"{i}. {p} 🔼 (Maior)")
            elif p > numero_secreto:
                st.write(f"{i}. {p} 🔽 (Menor)")

# Inicializar o banco de dados
init_db()

# Título com estilo personalizado
st.markdown("<h1 class='main-header'>🎯 Jogo de Adivinhação</h1>", unsafe_allow_html=True)

# Instruções detalhadas do jogo
with st.expander("📜 Como jogar (Clique para expandir)"):
    st.markdown("""
    <div class="instructions">
    <h3>Bem-vindo ao Jogo de Adivinhação!</h3>
    
    <h4>Regras do jogo:</h4>
    <ol>
        <li><strong>Objetivo:</strong> Adivinhar o número secreto com o menor número de tentativas possível.</li>
        <li><strong>Sistema de vidas:</strong> Você começa com um número de vidas que varia conforme o nível:
            <ul>
                <li>Nível Fácil: 7 vidas (número entre 1-50)</li>
                <li>Nível Médio: 5 vidas (número entre 1-100)</li>
                <li>Nível Difícil: 3 vidas (número entre 1-200)</li>
            </ul>
        </li>
        <li><strong>Como jogar:</strong>
            <ul>
                <li>Digite seu nome para começar</li>
                <li>Escolha o nível de dificuldade</li>
                <li>Digite um número no campo de palpite</li>
                <li>Clique em "Palpitar" para verificar</li>
                <li>Você receberá dicas se o número secreto é maior ou menor que seu palpite</li>
                <li>A cada tentativa incorreta, você perde uma vida (❤️)</li>
                <li>Se suas vidas acabarem, você perde o jogo</li>
            </ul>
        </li>
        <li><strong>Dicas:</strong> O jogo fornecerá dicas de "quente" ou "frio" para ajudar você a se aproximar do número secreto.</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

# Inicializar variáveis de sessão
if 'numero_secreto' not in st.session_state:
    st.session_state.numero_secreto = None
if 'tentativas' not in st.session_state:
    st.session_state.tentativas = 0
if 'inicio_jogo' not in st.session_state:
    st.session_state.inicio_jogo = None
if 'vidas' not in st.session_state:
    st.session_state.vidas = 0
if 'vidas_iniciais' not in st.session_state:
    st.session_state.vidas_iniciais = 0
if 'jogo_encerrado' not in st.session_state:
    st.session_state.jogo_encerrado = False
if 'nome_jogador' not in st.session_state:
    st.session_state.nome_jogador = ""
if 'palpites' not in st.session_state:
    st.session_state.palpites = []

# Formulário para iniciar o jogo
with st.form("inicio"):
    st.session_state.nome_jogador = st.text_input("Digite seu nome:", value=st.session_state.nome_jogador)
    nivel = st.selectbox("Escolha o nível de dificuldade:", ["Fácil", "Médio", "Difícil"])
    iniciar = st.form_submit_button("Iniciar Jogo")

if iniciar and st.session_state.nome_jogador:
    # Configurar jogo baseado no nível
    if nivel == "Fácil":
        st.session_state.numero_secreto = random.randint(1, 50)
        st.session_state.vidas_iniciais = st.session_state.vidas = 10
    elif nivel == "Médio":
        st.session_state.numero_secreto = random.randint(1, 100)
        st.session_state.vidas_iniciais = st.session_state.vidas = 8
    else:  # Difícil
        st.session_state.numero_secreto = random.randint(1, 200)
        st.session_state.vidas_iniciais = st.session_state.vidas = 6
    
    st.session_state.tentativas = 0
    st.session_state.inicio_jogo = time.time()
    st.session_state.jogo_encerrado = False
    st.success(f"Jogo iniciado! Nível: {nivel}. Boa sorte, {st.session_state.nome_jogador}!")
elif iniciar and not st.session_state.nome_jogador:
    st.warning("Por favor, digite seu nome para começar.")

# Se o jogo foi iniciado
if st.session_state.numero_secreto is not None and not st.session_state.jogo_encerrado:
    st.markdown(f"<div class='heart-container'>{exibir_vidas(st.session_state.vidas, st.session_state.vidas_iniciais)}</div>", 
                unsafe_allow_html=True)
    
    with st.form("palpite"):
        palpite = st.number_input("Digite seu palpite:", min_value=1, 
                                 max_value=200 if nivel == "Difícil" else 100 if nivel == "Médio" else 50,
                                 step=1)
        enviar = st.form_submit_button("Palpitar")
    
        if enviar:
            st.session_state.tentativas += 1
            st.session_state.palpites.append(palpite)  # Adiciona o palpite à lista
        
            # Mostra os palpites anteriores
            st.write(f"Você já digitou os números: {', '.join(map(str, st.session_state.palpites))}")
            
            if palpite == st.session_state.numero_secreto:
                tempo_total = time.time() - st.session_state.inicio_jogo
                st.session_state.jogo_encerrado = True
                st.balloons()
                st.success(f"🎉 Parabéns {st.session_state.nome_jogador}! Você acertou em {st.session_state.tentativas} tentativas!")
                st.markdown(f"<div class='highlight'>Tempo total: {tempo_total:.2f} segundos</div>", unsafe_allow_html=True)
                # Esta linha deve estar chamando a função correta:
                salvar_vencedor(st.session_state.nome_jogador, st.session_state.tentativas, tempo_total, nivel, st.session_state.vidas)
            else:
                st.session_state.vidas -= 1
                if st.session_state.vidas <= 0:
                    st.session_state.jogo_encerrado = True
                    st.markdown(f"<div class='game-over'>😢 Game Over! O número secreto era {st.session_state.numero_secreto}</div>", 
                                unsafe_allow_html=True)
                else:
                    dica = "🔽 Menor" if palpite > st.session_state.numero_secreto else "🔼 Maior"
                    st.warning(f"{dica} que {palpite}")
                    st.info(gerar_dica(palpite, st.session_state.numero_secreto, nivel))
            
# limpeza da lista de palpites quando o jogo for reiniciado            
if iniciar and st.session_state.nome_jogador:
    # Configurar jogo baseado no nível
    if nivel == "Fácil":
        st.session_state.numero_secreto = random.randint(1, 50)
        st.session_state.vidas_iniciais = st.session_state.vidas = 10
    elif nivel == "Médio":
        st.session_state.numero_secreto = random.randint(1, 100)
        st.session_state.vidas_iniciais = st.session_state.vidas = 8
    else:  # Difícil
        st.session_state.numero_secreto = random.randint(1, 200)
        st.session_state.vidas_iniciais = st.session_state.vidas = 6
    
    st.session_state.tentativas = 0
    st.session_state.palpites = []  # Limpa os palpites anteriores
    st.session_state.inicio_jogo = time.time()
    st.session_state.jogo_encerrado = False
    st.success(f"Jogo iniciado! Nível: {nivel}. Boa sorte, {st.session_state.nome_jogador}!")

# Mostrar ranking
mostrar_ranking()
