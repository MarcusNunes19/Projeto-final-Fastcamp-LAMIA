import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.prebuilt import create_react_agent

from src.router.message_classifier import message_router
from src.summarizer.summarizer import summarizer
from src.utils.utils import save_response_pdf

load_dotenv()

# Meu agente
model = ChatGroq(
    groq_api_key = os.getenv("GROQ_API_KEY") ,
    model_name= "openai/gpt-oss-120b",
    temperature= 0,
)

# Minha Tool
search = DuckDuckGoSearchResults()
tools = [search]

agent = create_react_agent(model, tools)

config = {"configurable": {
    "thread_id" : "1"
}}

def call_agent(query: str):
    """
    Executa o agente:
      - Se for fora do escopo → retorna mensagem direta
      - Caso contrário → executa fluxo completo (PDF + resumo)
    """
    # chama o message_router
    response = message_router(model, agent, query, config)

    # Se for fora do escopo, retorna mensagem direta e encerra
    if response == "FORA_DO_ESCOPO":
        return "Desculpe, não sou capaz de responder isso. Se precisar comprar ou pedir informações sobre um livro, estou à disposição."

    # Caso contrário, segue o fluxo normal
    if isinstance(response, dict) and "messages" in response:
        for message in response["messages"]:
            print(f"=========={message.type}==========")
            print(message.content, "\n")
        content_text = response["messages"][-1].content
    elif isinstance(response, list):
        for msg in response:
            print(f"=========={msg.type}==========")
            print(msg.content, "\n")
        content_text = response[-1].content
    else:
        content_text = str(response)

    # Salva o PDF completo (RAG)
    save_response_pdf(query, content_text, output_path="PDF_RAG.pdf")

    # Chama o sumarizador
    resumo_final = summarizer(model, query, "PDF_RAG.pdf", output_path="resumo.pdf")

    return resumo_final

