import os
import spacy
from langchain_core.messages import HumanMessage
from utils.utils import load_prompt, load_prahses

# SpaCy embeddings
nlp = spacy.load("pt_core_news_md")

#INFO/COMPRA Prompt
bibliotecario_prompt = load_prompt("src/prompts/classify.txt")

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

# Embeddings
def spacy_classifier(user_input: str, exemplos: dict) -> str:
    doc_input = nlp(user_input)
    scores = {
        cat: max(doc_input.similarity(nlp(frase)) for frase in frases)
        for cat, frases in exemplos.items()
    }
    return max(scores, key=scores.get)


def message_classifier(user_input: str) -> str:
    """Decide a categoria usando SOMENTE embeddings"""
    # Escopo
    scope_result = spacy_classifier(user_input, exemplos_escopo)
    if scope_result == "FORA_DO_ESCOPO":
        return "FORA_DO_ESCOPO"
    # INFO/COMPRA
    return spacy_classifier(user_input, exemplos_classi)


# Roteador de ação
def message_router(model, agent, query: str, config: dict):
    """
    Usa embeddings para classificar,
    mas gera respostas sempre baseadas nos PROMPTS definidos.
    """
    
    #  Classificação de categoria
    categoria = message_classifier(query)
    print(f"[Classificação Final] {categoria}")

    if categoria == "COMPRA":
        print("[ROTA] COMPRA")
        prompt_text = bibliotecario_prompt.format(user_input=query, memory="")
        response = agent.invoke({"messages": HumanMessage(content=prompt_text)}, config)
       

    elif categoria == "INFO":
        print("[ROTA] INFO")
        prompt_text = bibliotecario_prompt.format(user_input=query, memory="")
        response = model.invoke([HumanMessage(content=prompt_text)])
        

    elif categoria == "FORA_DO_ESCOPO":
        print("[ROTA] Fora do escopo → resposta neutra")
        prompt_text = bibliotecario_prompt.format(user_input=query, memory="")
        response = model.invoke([HumanMessage(content=prompt_text)])

    else:
        print("[ROTA] Fallback → INFO")
        prompt_text = bibliotecario_prompt.format(user_input=query, memory="")
        response = model.invoke([HumanMessage(content=prompt_text)])

    return response