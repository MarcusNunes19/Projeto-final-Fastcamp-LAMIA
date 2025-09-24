import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
from agent import call_agent

# Caminho da imagem (ajuste conforme o local real)
IMAGE_PATH = "Imagens/livrinho.png"

# --- TÍTULO ---
st.title("Bibliotecário virtual 📚")

# --- ESTILO PERSONALIZADO ---
st.markdown(
    """
    <style>
        .centered-img {
            display: flex;
            justify-content: center;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        .intro-text {
            text-align: center;
            font-size: 1rem;
            color: #444;
            line-height: 1.5;
            margin: 15px auto 30px;
            max-width: 750px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- IMAGEM CENTRAL ---
st.markdown('<div class="centered-img">', unsafe_allow_html=True)
st.image(IMAGE_PATH, width=220, caption="Assistente de biblioteca virtual", use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)

# --- TEXTO INTRODUTÓRIO (TOM MAIS NEUTRO) ---
st.markdown(
    """
    <div class="intro-text">
        <p>
        Este chatbot foi desenvolvido como parte de um experimento para aprimorar agentes de linguagem aplicados ao contexto de bibliotecas digitais.
        Ele é capaz de buscar informações sobre livros e sugerir links de compra, priorizando fontes válidas e seguras.
        </p>
        <p>
        A proposta surgiu a partir de observações sobre limitações em modelos amplamente utilizados, que frequentemente retornavam resultados imprecisos ou pouco confiáveis.
        Para melhorar a consistência das respostas, o agente utiliza técnicas de classificação baseadas em <em>embeddings</em> do SpaCy e princípios de <em>prompt engineering</em>.
        </p>
        <p>
        Embora ainda em fase de aprimoramento, o objetivo é oferecer um assistente capaz de auxiliar leitores de forma prática e informativa.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- HISTÓRICO DE MENSAGENS ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configurações")
    if st.button("🗑️ Limpar mensagens"):
        st.session_state["messages"] = []
        st.rerun()

# --- EXIBIR MENSAGENS ANTERIORES ---
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# --- INPUT DO USUÁRIO ---
if query := st.chat_input("Como posso ajudar você hoje? Deseja comprar ou saber mais sobre algum livro específico?"):
    st.session_state["messages"].append({"role": "user", "content": query})
    st.chat_message("user").write(query)

    resumo = call_agent(query)

    st.session_state["messages"].append({"role": "assistant", "content": resumo})
    st.chat_message("assistant").write(resumo)
