import streamlit as st
import time
import random
import pandas as pd
import os

# Configuração da página
st.set_page_config(
    page_title="Jogo de Adivinhação",
    page_icon="🎮",
    layout="centered"
)

# CSS personalizado
st.markdown("""
<style>
    .highlight {
        padding: 10px;
        background-color: #f0f2f6;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
    }
    .game-over {
        color: red;
        font-size: 24px;
        font-weight: bold;
        padding: 10px;
        margin: 10px 0;
    }
    .heart-container {
        font-size: 24px;
        margin: 10px 0;
    }
    .stApp {
        background-color: #f5f7f9;
    }
    h1 {
        color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização das variáveis de estado da sessão
if 'jogo_iniciado' not in st.session_state:
    st.session_state.jogo_iniciado = False
if 'jogo_encerrado' not in st.session_state:
    st.session_state.jogo_encerrado = False
if 'numero_secreto' not in st.session_state:
    st.session_state.numero_secreto = None
if 'tentativas' not in st.session_state:
    st.session_state.tentativas = 0
if 'vidas' not in st.session_state:
    st.session_state.vidas = 5
if 'vidas_iniciais' not in st.session_state:
    st.session_state.vidas_iniciais = 5
if 'nome_jogador' not in st.session_state:
    st.session_state.nome_jogador = ""
if 'inicio_jogo' not in st.session_state:
    st.session_state.inicio_jogo = 0
if 'palpites' not in st.session_state:
    st.session_state.palpites = []

# Funções do jogo
def iniciar_jogo(nome, nivel):
    """Inicializa um novo jogo"""
    max_numero = 50  # Fácil
    vidas = 7
    
    if nivel == "Médio":
        max_numero = 100
        vidas = 5
    elif nivel == "Difícil":
        max_numero = 200
        vidas = 3
    
    st.session_state.nome_jogador = nome
    st.session_state.numero_secreto = random.randint(1, max_numero)
    st.session_state.jogo_iniciado = True
    st.session_state.jogo_encerrado = False
    st.session_state.tentativas = 0
    st.session_state.vidas = vidas
    st.session_state.vidas_iniciais = vidas
    st.session_state.inicio_jogo = time.time()
    st.session_state.palpites = []

def exibir_vidas(vidas, vidas_iniciais):
    """Exibe corações representando as vidas restantes"""
    return "❤️" * vidas + "🖤" * (vidas_iniciais - vidas)

def gerar_dica(palpite, numero_secreto, nivel):
    """Gera uma dica baseada no palpite e no nível de dificuldade"""
    diferenca = abs(palpite - numero_secreto)
    
    if nivel == "Fácil":
        if diferenca > 20:
            return "Está muito longe!"
        elif diferenca > 10:
            return "Está longe!"
        elif diferenca > 5:
            return "Está se aproximando!"
        else:
            return "Está muito perto!"
    elif nivel == "Médio":
        if diferenca > 30:
            return "Está muito longe!"
        elif diferenca > 15:
            return "Está longe!"
        elif diferenca > 5:
            return "Está se aproximando!"
        else:
            return "Está perto!"
    else:  # Difícil
        if diferenca > 50:
            return "Está muito longe!"
        elif diferenca > 25:
            return "Está longe!"
        else:
            return "Sem mais dicas no nível difícil!"

def mostrar_historico_palpites(palpites, numero_secreto):
    """Mostra o histórico de palpites do jogador"""
    if palpites:
        st.write("### Seus palpites anteriores:")
        for i, p in enumerate(palpites, 1):
            if p < numero_secreto:
                st.write(f"{i}. {p} 🔼 (Maior)")
            elif p > numero_secreto:
                st.write(f"{i}. {p} 🔽 (Menor)")

def salvar_vencedor(nome, tentativas, tempo, nivel, vidas):
    """Salva os dados do vencedor em um arquivo CSV"""
    data = {
        'Nome': [nome],
        'Tentativas': [tentativas],
        'Tempo (s)': [round(tempo, 2)],
        'Nível': [nivel],
        'Vidas Restantes': [vidas]
    }
    
    df = pd.DataFrame(data)
    
    # Verifica se o arquivo já existe
    if os.path.exists('ranking.csv'):
        ranking = pd.read_csv('ranking.csv')
        ranking = pd.concat([ranking, df], ignore_index=True)
    else:
        ranking = df
    
    ranking.to_csv('ranking.csv', index=False)

def mostrar_ranking():
    """Mostra o ranking dos jogadores"""
    if os.path.exists('ranking.csv'):
        st.write("## 🏆 Ranking dos Jogadores")
        ranking = pd.read_csv('ranking.csv')
        
        # Ordena por tentativas (menos é melhor) e tempo (menos é melhor)
        ranking = ranking.sort_values(by=['Tentativas', 'Tempo (s)'])
        
        # Exibe apenas os 10 melhores
        st.dataframe(ranking.head(10), use_container_width=True)

# Interface principal
st.title("🎮 Jogo de Adivinhação")
st.write("Tente adivinhar o número secreto!")

# Sidebar para configurações do jogo
with st.sidebar:
    st.header("Configurações")
    
    if not st.session_state.jogo_iniciado or st.session_state.jogo_encerrado:
        nome = st.text_input("Seu nome:", key="input_nome")
        nivel = st.selectbox("Nível de dificuldade:", ["Fácil", "Médio", "Difícil"])
        
        if st.button("Iniciar Jogo"):
            if nome:
                iniciar_jogo(nome, nivel)
            else:
                st.error("Por favor, digite seu nome para começar.")
    
    if st.session_state.jogo_iniciado and not st.session_state.jogo_encerrado:
        if st.button("Desistir"):
            st.session_state.jogo_encerrado = True
            st.info(f"Você desistiu. O número secreto era {st.session_state.numero_secreto}")
    
    if st.session_state.jogo_encerrado:
        if st.button("Novo Jogo"):
            st.session_state.jogo_iniciado = False

# Área principal do jogo
if not st.session_state.jogo_iniciado:
    st.warning
