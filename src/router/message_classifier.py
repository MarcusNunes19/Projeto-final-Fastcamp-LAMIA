import os
import spacy
from langchain_core.messages import HumanMessage
from utils.utils import load_prompt, load_prahses

# SpaCy embeddings
nlp = spacy.load("pt_core_news_md")

#INFO/COMPRA Prompt
bibliotecario_prompt = load_prompt("src/prompts/classify.txt")
prompt_foraEscopo = load_prompt("src/prompts/classify_noScope.txt") 

# Exemplos para comparação de similaridade
exemplos_escopo = {
    "DENTRO_DO_ESCOPO": load_prahses("src/embeddings_aux/scope_examples.txt"),
    "FORA_DO_ESCOPO": load_prahses("src/embeddings_aux/no_scope_examples.txt")
}

#Exemplos para comparação de similaridade
exemplos_classi = {
    "INFO": load_prahses("src/embeddings_aux/info_examples.txt"),
    "COMPRA": load_prahses("src/embeddings_aux/buy_examples.txt")
}

def message_classifier(user_input: str) -> str:
    """Classifica a mensagem diretamente usando embeddings"""
    doc_input = nlp(user_input)

    # Classificação de Escopo (Dentro do escopo/ Fora do escopo)
    scores_escopo = {
        cat: max(doc_input.similarity(nlp(frase)) for frase in frases)
        for cat, frases in exemplos_escopo.items()
    }
    scope_result = max(scores_escopo, key=scores_escopo.get)

    # Se for fora do escopo a função já acaba
    if scope_result == "FORA_DO_ESCOPO":
        return "FORA_DO_ESCOPO"

    #Classificação de INFO/COMPRA(Dentro do escopo)
    scores_classi = {
        cat: max(doc_input.similarity(nlp(frase)) for frase in frases)
        for cat, frases in exemplos_classi.items()
    }
    return max(scores_classi, key=scores_classi.get)

def message_router(model, agent, query: str, config: dict):
    """
    Usa embeddings para classificar,
    mas gera respostas sempre baseadas nos PROMPTS definidos.
    """

    #  Classificação de categoria
    categoria = message_classifier(query)
    print(f"[Classificação Final] {categoria}")

    # Fora do escopo --> resposta direta, sem chamar modelo
    if categoria == "FORA_DO_ESCOPO":
        print("[ROTA] Fora do escopo → resposta direta")
        return "FORA_DO_ESCOPO"

    # Dentro do escopo --> Providenciar links de compra
    if categoria == "COMPRA":
        print("[ROTA] COMPRA")
        prompt_text = bibliotecario_prompt.format(user_input=query, memory="")
        response = agent.invoke({"messages": HumanMessage(content=prompt_text)}, config)
       
    # Dentro do Escopo --> Dar informações
    elif categoria == "INFO":
        print("[ROTA] INFO")
        prompt_text = bibliotecario_prompt.format(user_input=query, memory="")
        response = model.invoke([HumanMessage(content=prompt_text)])
        
    # Fallback → INFO
    else:
        print("[ROTA] Fallback → INFO")
        prompt_text = bibliotecario_prompt.format(user_input=query, memory="")
        response = model.invoke([HumanMessage(content=prompt_text)])

    return response