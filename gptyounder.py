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

# UI para inserção da chave da API da OpenAI
with st.sidebar:
    openai_api_key = st.text_input("Chave da API da OpenAI", key="chatbot_api_key", type="password")
    if uploaded_file := st.file_uploader("Carregar documento para resumo", type=["pdf", "xlsx", "docx"]):
        st.session_state["document_content"] = process_file(uploaded_file)

def process_file(uploaded_file):
    """Processa o arquivo carregado e retorna seu texto."""
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return extract_text_from_excel(uploaded_file)

def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read()) as doc:
        return " ".join(page.get_text() for page in doc)

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return '\n'.join(para.text for para in doc.paragraphs)

def extract_text_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df.to_string(index=False)

st.title("💬 Chatbot com Resumo de Documentos")

# Entrada de texto do usuário
prompt = st.text_input("Digite sua pergunta ou 'resumir documento':")

if prompt and openai_api_key:
    if prompt.lower() == "resumir documento" and st.session_state["document_content"]:
        prompt = st.session_state["document_content"]
        summarize_document(openai_api_key, prompt)
    else:
        converse_with_openai(openai_api_key, prompt)

def summarize_document(api_key, document_text):
    # Aqui você pode adaptar para chamar a API da OpenAI e solicitar um resumo do texto do documento
    pass

def converse_with_openai(api_key, prompt):
    # Aqui você pode usar a funcionalidade do código original para conversar com o OpenAI
    pass
