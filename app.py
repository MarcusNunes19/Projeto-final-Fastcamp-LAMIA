import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
from agent import call_agent

st.title("Bibliotecário virtual 📚")

# Loads the mesage history 
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Button to delete all mesages 
with st.sidebar:
    st.header("Configurações")
   
    if st.button("🗑️ Limpar mensagens"):
        st.session_state["messages"] = []
        st.rerun()  

# It exibits the previous messages 
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# User's input
if query := st.chat_input("Como posso ajudar você hoje? Deseja comprar ou saber mais sobre algum livro específico?"):
    # Adds the user's input to the history
    st.session_state["messages"].append({"role": "user", "content": query})
    st.chat_message("user").write(query)

    # Calls the agent but only retrieves the summarized information
    resumo = call_agent(query)

    # Adds the response to the history
    st.session_state["messages"].append({"role": "assistant", "content": resumo})
    st.chat_message("assistant").write(resumo)
