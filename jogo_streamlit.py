import streamlit as st
import pandas as pd
import time
import os
import random

# Configuração da página
st.set_page_config(
    page_title="Jogo de Adivinhação",
    page_icon="🎮",
    layout="centered"
)

# CSS personalizado
st.markdown("""
<style>
    .palpites-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 20px;
    }
    .palpite-item {
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
    }
    .palpite-menor {
        background-color: #ffcccc;
    }
    .palpite-maior {
        background-color: #cce5ff;
    }
    .stButton button {
        width: 100%;
        font-size: 18px;
    }
    .game-header {
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização de variáveis de estado
if 'numero_secreto' not in st.session_state:
    st.session_state.numero_secreto = random.randint(1, 100)
if 'palpites' not in st.session_state:
    st.session_state.palpites = []
if 'jogo_iniciado' not in st.session_state:
    st.session_state.jogo_iniciado = False
if 'tempo_inicio' not in st.session_state:
    st.session_state.tempo_inicio = None
if 'vidas' not in st.session_state:
    st.session_state.vidas = 5
if 'nivel' not in st.session_state:
    st.session_state.nivel = "Médio"
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'vitoria' not in st.session_state:
    st.session_state.vitoria = False
if 'nome_jogador' not in st.session_state:
    st.session_state.nome_jogador = ""

def reiniciar_jogo():
    """Reinicia o jogo com novos valores"""
    st.session_state.numero_secreto = random.randint(1, 100)
    st.session_state.palpites = []
    st.session_state.jogo_iniciado = False
    st.session_state.tempo_inicio = None
    st.session_state.game_over = False
    st.session_state.vitoria = False
    
    # Ajusta vidas conforme o nível
    if st.session_state.nivel == "Fácil":
        st.session_state.vidas = 10
    elif st.session_state.nivel == "Médio":
        st.session_state.vidas = 8
    else:  # Difícil
        st.session_state.vidas = 6

def verificar_palpite(palpite, numero_secreto):
    """Verifica se o palpite está correto e retorna uma mensagem"""
    if palpite == numero_secreto:
        return True, "Parabéns! Você acertou! 🎉"
    
    # Reduz uma vida
    st.session_state.vidas -= 1
    
    # Verifica se o jogo acabou
    if st.session_state.vidas <= 0:
        return False, f"Game Over! O número secreto era {numero_secreto}. 😢"
    
    # Gera dica baseada no nível
    dica = gerar_dica(palpite, numero_secreto, st.session_state.nivel)
    return False, f"Errou! {dica} Vidas restantes: {st.session_state.vidas}"

def gerar_dica(palpite, numero_secreto, nivel):
    """Gera uma dica baseada no nível de dificuldade"""
    diferenca = abs(palpite - numero_secreto)
    
    if palpite < numero_secreto:
        direcao = "maior"
    else:
        direcao = "menor"
    
    if nivel == "Fácil":
        return f"O número secreto é {direcao}. Diferença: {diferenca}"
    elif nivel == "Médio":
        if diferenca > 20:
            return f"O número secreto é {direcao} e está muito longe!"
        elif diferenca > 10:
            return f"O número secreto é {direcao} e está longe!"
        else:
            return f"O número secreto é {direcao} e está perto!"
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
        
        # Container para os palpites
        st.markdown("<div class='palpites-container'>", unsafe_allow_html=True)
        
        for p in palpites:
            if p < numero_secreto:
                st.markdown(f"<span class='palpite-item palpite-menor'>{p} 🔼</span>", unsafe_allow_html=True)
            elif p > numero_secreto:
                st.markdown(f"<span class='palpite-item palpite-maior'>{p} 🔽</span>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Mostrar números já tentados
        st.write("#### Números já tentados:")
        st.write(f"{sorted(palpites)}")

def salvar_vencedor(nome, tentativas, tempo, nivel, vidas):
    """Salva os dados do vencedor em um arquivo CSV"""
    data = {
        'Nome': [nome],
        'Tentativas': [tentativas],
        'Tempo (s)': [round(tempo, 2)],
        'Nível': [nivel],
        'Vidas Restantes': [vidas],
        'Data': [time.strftime("%Y-%m-%d %H:%M:%S")]
    }
    
    df = pd.DataFrame(data)
    
    # Verifica se o arquivo já existe
    if os.path.exists('ranking.csv'):
        ranking = pd.read_csv('ranking.csv')
        ranking = pd.concat([ranking, df], ignore_index=True)
    else:
        ranking = df
    
    ranking.to_csv('ranking.csv', index=False)

def calcular_pontuacao(tentativas, tempo, nivel, vidas):
    """Calcula a pontuação baseada nas tentativas, tempo, nível e vidas restantes"""
    # Fator de dificuldade
    if nivel == "Fácil":
        fator_nivel = 1
    elif nivel == "Médio":
        fator_nivel = 2
    else:  # Difícil
        fator_nivel = 3
    
    # Cálculo da pontuação
    pontuacao_base = 1000
    penalidade_tentativas = tentativas * 10
    penalidade_tempo = tempo * 2
    bonus_vidas = vidas * 50
    
    pontuacao = (pontuacao_base - penalidade_tentativas - penalidade_tempo + bonus_vidas) * fator_nivel
    
    return max(0, pontuacao)  # Garante que a pontuação não seja negativa

def mostrar_ranking():
    """
