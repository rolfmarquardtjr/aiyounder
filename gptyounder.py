import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF, conhecida também como fitz
import os

# Inicialização e configuração da chave da API da OpenAI
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

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

def summarize_content(document_content, max_tokens=1024):
    """Resume o conteúdo do documento para um tamanho gerenciável."""
    if len(document_content) > max_tokens:
        # Aqui você poderia adicionar uma lógica para resumir o conteúdo
        return document_content[:max_tokens]  # Simples truncamento como exemplo
    return document_content

def send_message(user_input, document_content):
    """Envia a mensagem do usuário e o conteúdo resumido do documento para a OpenAI."""
    context = summarize_content(document_content)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Erro ao consultar a OpenAI: {str(e)}"

# Interface do usuário
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

with st.sidebar:
    st.image("https://younder.com.br/wp-content/uploads/2023/03/Logotipo-Younder-horizontal-principal-1-1024x447.png", width=300)
    st.header("Upload de Documentos")
    file_types = ["PDF", "Excel", "Word"]
    file_type = st.selectbox("Tipo de Documento", ["Escolher"] + file_types)
    if file_type != "Escolher":
        uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
        if uploaded_file:
            document_content = process_file(uploaded_file, file_type)
            st.session_state['document_content'] = document_content

st.title("Chat com ChatGPT")
user_input = st.text_input("Digite sua pergunta relacionada ao documento:", "")

if st.button("Enviar") and user_input:
    assistant_response = send_message(user_input, st.session_state.get('document_content', ''))
    st.session_state.messages.append(f"Você: {user_input}")
    st.session_state.messages.append(f"Assistente: {assistant_response}")

for message in st.session_state.messages:
    st.text(message)
