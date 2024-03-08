import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF, conhecida também como fitz
import os

# Acessar a chave da API da OpenAI de Secrets no Streamlit Cloud
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
    """Envia a mensagem do usuário e o conteúdo do documento para a OpenAI e retorna a resposta."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": document_content},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Erro ao consultar a OpenAI: {str(e)}"

# Adicionando o logo
st.image("https://younder.com.br/wp-content/uploads/2023/03/Logotipo-Younder-horizontal-principal-1-1024x447.png", width=300)

# UI para o chat
st.title("Chat com a Younder GPT")

# Utilizando st.form para permitir o envio com Enter
with st.form("chat_form"):
    user_input = st.text_input("Digite sua pergunta relacionada ao documento:", "")
    submit_button = st.form_submit_button("Enviar")

if submit_button and user_input:
    if 'document_content' in st.session_state:
        assistant_response = send_message(user_input, st.session_state['document_content'])
        st.session_state['messages'].append(f"Você: {user_input}")
        st.session_state['messages'].append(f"Assistente: {assistant_response}")

for message in st.session_state.get('messages', []):
    st.text(message)

# Sidebar para upload de documentos
with st.sidebar:
    st.header("Upload de Documentos")
    file_types = ["PDF", "Excel", "Word"]
    file_type = st.selectbox("Tipo de Documento", ["Escolher"] + file_types)
    if file_type != "Escolher":
        uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
        if uploaded_file:
            document_content = process_file(uploaded_file, file_type)
            st.session_state['document_content'] = document_content
            st.text_area("Prévia do documento", value=document_content[:500] + "...", height=150, disabled=True)
