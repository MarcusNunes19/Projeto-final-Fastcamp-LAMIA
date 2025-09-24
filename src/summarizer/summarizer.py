from langchain_core.messages import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from utils.utils import load_pdf_text, save_response_pdf, load_prompt

def summarizer(model, query: str, pdf_path: str, output_path="resumo.pdf", top_k=3, embedding_model=None):
    """
    Summarizer com RAG:
      - Extrai o texto do PDF
      - Cria embeddings e um retriever
      - Recupera trechos relevantes para a query
      - Usa seu prompt customizado para gerar a resposta final
    """
    # Pega todas as informações contidas no PDF de RAG
    content = load_pdf_text(pdf_path)

    # Divide o texto em chuncks para os embeddings
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text(content)

    # Cria os embeddings e o vetor de busca
    embeddings_model = embedding_model or HuggingFaceEmbeddings()
    vectorstore = FAISS.from_texts(chunks, embeddings_model)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": top_k})

    # Pega as informações mais relevantes
    relevant_chunks = retriever.get_relevant_documents(query)
    context_text = "\n".join([chunk.page_content for chunk in relevant_chunks])

    # carrega o sumarizador e o pdf original
    base_prompt = load_prompt("src/prompts/summarize_text.txt")
    prompt = f"""{base_prompt}\n\nUse apenas o seguinte contexto 
    e nada mais para responder à pergunta do usuário:\n{context_text}\n\nPergunta: {query}"""

    # chama o modelo
    response = model.invoke([HumanMessage(content=prompt)])

    # Extrai o texto de uma maneira limpa
    resumo_texto = response.content if hasattr(response, "content") else str(response)

    # Salva o resumo em um pdf
    save_response_pdf("Resumo do relatório.pdf", resumo_texto, output_path=output_path)

    print(f"[RAG SUMMARIZER] Resumo salvo em {output_path}")
    return resumo_texto
