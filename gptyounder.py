import streamlit as st
import pandas as pd
import docx
import fitz  # PyMuPDF
from openai import OpenAI

# Inicialização do estado da sessão para mensagens e conteúdo do documento
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Como posso ajudá-lo?"}]
if "document_content" not in st.session_state:
    st.session_state["document_content"] = ""

# Função para processar o arquivo carregado
def process_file(uploaded_file):
    """Processa o arquivo carregado e retorna seu texto."""
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return extract_text_from_excel(uploaded_file)

# Funções dedicadas para extrair texto dos formatos de arquivo suportados
def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.getbuffer()) as doc:
        return " ".join(page.get_text() for page in doc)

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return '\n'.join(para.text for para in doc.paragraphs)

def extract_text_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df.to_string(index=False)

# UI para inserção da chave da API da OpenAI e upload de arquivo
with st.sidebar:
    openai_api_key = st.text_input("Chave da API da OpenAI", type="password")
    
    uploaded_file = st.file_uploader("Carregar documento para resumo", type=["pdf", "xlsx", "docx"])
    if uploaded_file:
        st.session_state["document_content"] = process_file(uploaded_file)

# Funções para interagir com a API da OpenAI
def summarize_document(api_key, document_text):
    # Implemente a lógica para chamar a API da OpenAI e solicitar o resumo
    st.write("Resumo do documento:")
    st.write(document_text)  # Placeholder para o verdadeiro resumo

def converse_with_openai(api_key, prompt):
    # Implemente a lógica para conversar com a API da OpenAI
    st.write("Resposta do chatbot:")
    st.write(prompt)  # Placeholder para a verdadeira resposta

# Interface de entrada de texto do usuário
st.title("💬 Chatbot com Resumo de Documentos")

prompt = st.text_input("Digite sua pergunta ou 'resumir documento':")

# Lógica principal para lidar com a entrada do usuário e a chave da API
if prompt and openai_api_key:
    if prompt.lower() == "resumir documento" and st.session_state["document_content"]:
        document_text = st.session_state["document_content"]
        summarize_document(openai_api_key, document_text)
    else:
        converse_with_openai(openai_api_key, prompt)
