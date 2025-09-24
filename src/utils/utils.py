from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import fitz 

#Uma função que carrega frases, feita para carregar as frases dos embeddings_aux
def load_prahses(file_path: str) -> list:

    file = open(file_path, "r")
    read = file.readlines()
    prhase_list = list()

    for line in read:
        if line[-1] == '\n':
            prhase_list.append(line[:-1])
    
    return prhase_list

#Uma função para carregar os prompts
def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

#Uma função para carregar o conteúdo dos pdfs
def load_pdf_text(path_pdf: str) ->str:
    """Extrai os textos dos pdfs usando o PyMuPDF"""

    doc= fitz.open(path_pdf)
    text= ""

    for page in doc:
        text+= page.get_text("text") + "\n"
    return text.strip()

#Uma função para salvar as respostas em um arquivo pdf
def save_response_pdf(query: str, content: str, output_path: str):
    
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b> Consulta do Usuário:</b>", styles["Heading3"]))
    story.append(Paragraph(query, styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b> Resposta do Agente:</b>", styles["Heading3"]))
    for paragrafo in content.split("\n\n"):
        story.append(Paragraph(paragrafo.strip(), styles["Normal"]))
        story.append(Spacer(1, 8))

    
    doc.build(story)
    print(f"[PDF] PDF salvo em: {output_path}")