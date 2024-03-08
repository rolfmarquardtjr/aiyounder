import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF

# Função para processar arquivos carregados e retornar texto
def process_file(uploaded_file, file_type):
    if file_type == "PDF":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            text = " ".join(page.get_text() for page in doc)
    elif file_type == "Excel":
        df = pd.read_excel(uploaded_file)
        text = df.to_string(index=False)
    elif file_type == "Word":
        doc = docx.Document(uploaded_file)
        text = '\n'.join(para.text for para in doc.paragraphs)
    return text

# Função para enviar mensagens e receber respostas
def send_message():
    message_text = st.session_state.user_input
    if message_text:
        st.session_state.messages.append(f"Você: {message_text}")
        openai_api_key = st.session_state.openai_api_key
        if openai_api_key:
            try:
                openai.api_key = openai_api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": st.session_state.document_content},
                              {"role": "user", "content": message_text}]
                )
                st.session_state.messages.append(f"Assistente: {response.choices[0].message['content']}")
            except Exception as e:
                st.session_state.messages.append(f"Assistente: Erro ao consultar a OpenAI: {e}")
        else:
            st.session_state.messages.append("Assistente: Por favor, insira a chave da API da OpenAI.")
        st.session_state.user_input = ''

# Sidebar para inserção da chave da API da OpenAI e upload de documentos
with st.sidebar:
    st.session_state.openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.header("Upload de Documentos")
    file_type = st.selectbox("Tipo de Documento", options=["", "PDF", "Excel", "Word"])
    if file_type:
        uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
        if uploaded_file:
            st.session_state.document_content = process_file(uploaded_file, file_type)
            st.text_area("Prévia do documento:", value=st.session_state.document_content, height=150)

# Inicializa as variáveis de estado da sessão
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''
if 'document_content' not in st.session_state:
    st.session_state.document_content = ''
if 'file_type' not in st.session_state:
    st.session_state.file_type = ''

# Área principal do chat
st.title("Chat")
for message in st.session_state.messages:
    st.text(message)

# Campo de entrada para o chat
st.text_input("Digite sua mensagem e pressione Enter:",
              key="user_input",
              on_change=send_message)

# Script para rolagem automática (atualizado para funcionar corretamente)
st.markdown("""
    <script>
        const messageBox = document.querySelector('.stTextInput');
        messageBox.scrollIntoView({behavior: 'smooth', block: 'end'});
    </script>
""", unsafe_allow_html=True)
