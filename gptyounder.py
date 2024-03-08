import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF
import os

# Função para processar arquivos carregados e retornar texto
def process_file(uploaded_file, file_type):
    text = ""
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
def send_message(user_input, document_content):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("Chave da API da OpenAI não encontrada. Configure a variável de ambiente OPENAI_API_KEY.")
        return "Chave da API da OpenAI não configurada."

    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": document_content},
                      {"role": "user", "content": user_input}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Erro ao consultar a OpenAI: {str(e)}"

# Inicialização das variáveis de estado da sessão
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''
if 'document_content' not in st.session_state:
    st.session_state.document_content = ''

# Sidebar para upload de documentos
with st.sidebar:
    st.header("Upload de Documentos")
    file_types = ["PDF", "Excel", "Word"]
    file_type = st.selectbox("Tipo de Documento", options=[""] + file_types)
    if file_type:
        uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
        if uploaded_file:
            st.session_state.document_content = process_file(uploaded_file, file_type)
            st.text_area("Prévia do documento:", value=st.session_state.document_content[:500] + "...", height=150)

# Área de chat principal dentro de um container com rolagem automática
st.title("Chat com ChatGPT")
user_input = st.text_input("Digite sua mensagem:", key="user_input")

if st.button("Enviar") and user_input:
    assistant_response = send_message(user_input, st.session_state.document_content)
    st.session_state.messages.append(f"Você: {user_input}")
    st.session_state.messages.append(f"Assistente: {assistant_response}")
    st.session_state.user_input = ''  # Limpar após envio

# Container de Chat
st.markdown("<div style='height: 400px; overflow-y: scroll; border: 1px solid #eee; padding: 10px;' id='chat-container'>", unsafe_allow_html=True)
for message in st.session_state.messages:
    st.markdown(f"<p>{message}</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Script para rolagem automática
st.markdown("""
<script>
    const chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
</script>
""", unsafe_allow_html=True)
