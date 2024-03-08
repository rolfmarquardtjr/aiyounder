import streamlit as st
import pandas as pd
import docx
import fitz  # PyMuPDF
from openai import OpenAI

# Função para processar o arquivo carregado
def process_file(uploaded_file, file_type):
    """Processa o arquivo carregado e retorna seu texto."""
    text = ""
    if file_type == "PDF":
        with fitz.open(stream=uploaded_file.read()) as doc:
            text = " ".join(page.get_text() for page in doc)
    elif file_type == "Excel":
        df = pd.read_excel(uploaded_file)
        text = df.to_string(index=False)
    elif file_type == "Word":
        doc = docx.Document(uploaded_file)
        text = '\n'.join(para.text for para in doc.paragraphs)
    return text

# Função para enviar texto à API do ChatGPT e obter um resumo
def get_summary(text, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Resuma o seguinte texto:"}, {"role": "user", "content": text}]
    )
    return response.choices[0].message['content']

# Solicita a chave da API da OpenAI através da interface do Streamlit
with st.sidebar:
    openai_api_key = st.text_input("Chave da API da OpenAI", key="chatbot_api_key", type="password")

# Adicionando o logo
st.image("https://younder.com.br/wp-content/uploads/2023/03/Logotipo-Younder-horizontal-principal-1-1024x447.png", width=300)

# UI para upload de documentos
st.title("💬 Chatbot da Younder")

# UI para upload de documentos
st.header("Upload de Documentos")
file_types = ["PDF", "Excel", "Word"]
file_type = st.selectbox("Tipo de Documento", file_types)
uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])

if uploaded_file and openai_api_key:
    document_content = process_file(uploaded_file, file_type)
    summary = get_summary(document_content, openai_api_key)
    st.write("Resumo do Documento:")
    st.write(summary)
else:
    if not openai_api_key:
        st.warning("Por favor, adicione sua chave da API da OpenAI para continuar.")

# O código para interações adicionais com o chatbot pode ser adicionado aqui
