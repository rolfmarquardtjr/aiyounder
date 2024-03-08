import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # Importação ajustada para PyMuPDF
import os

# Define a chave da API da OpenAI usando Secrets no Streamlit Cloud
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

def send_message(user_input, document_content):
    """Envia a mensagem do usuário para a OpenAI e retorna a resposta."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Erro ao consultar a OpenAI: {str(e)}"

# Sidebar para upload de documentos
with st.sidebar:
    st.image("https://younder.com.br/wp-content/uploads/2023/03/Logotipo-Younder-horizontal-principal-1-1024x447.png", width=300)
    st.header("Upload de Documentos")
    file_type = st.selectbox("Tipo de Documento", ["Escolher", "PDF", "Excel", "Word"])
    document_content = ""
    if file_type != "Escolher":
        uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
        if uploaded_file:
            document_content = process_file(uploaded_file, file_type)
            st.session_state['document_content'] = document_content

st.title("Chat com ChatGPT")

# Campo de entrada de texto que limpa após o envio e permite enviar com Enter
user_input = st.text_input("Digite sua pergunta relacionada ao documento:", "", on_change=send_message, args=(st.session_state.get('document_content', ''),), key="user_input")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Exibe as mensagens
for message in st.session_state['messages']:
    st.text(message)

# Funcionalidade para limpar a caixa de texto e enviar com Enter
if st.button("Enviar"):
    if user_input:
        assistant_response = send_message(user_input, st.session_state.get('document_content', ''))
        st.session_state['messages'].append(f"Você: {user_input}")
        st.session_state['messages'].append(f"Assistente: {assistant_response}")
        st.session_state.user_input = ''  # Limpa a caixa de texto
        st.experimental_rerun()  # Força a atualização da página para limpar a caixa de texto
