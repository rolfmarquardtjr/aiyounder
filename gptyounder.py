import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF

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

st.title("💬 Chat com ChatGPT")

# UI para upload de documentos
with st.sidebar:
    st.header("Upload de Documentos")
    file_types = ["PDF", "Excel", "Word"]
    file_type = st.selectbox("Tipo de Documento", ["Escolher"] + file_types)
    uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
    if uploaded_file and file_type != "Escolher":
        document_content = process_file(uploaded_file, file_type)
        st.session_state['document_content'] = document_content

# Inicialização do estado da sessão para mensagens
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "Como posso ajudá-lo?"}]

# Exibição das mensagens anteriores
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["content"], is_user=True)
    else:
        st.chat_message(msg["content"])

# Entrada de texto do usuário
user_input = st.chat_input("Digite sua pergunta ou peça para resumir o documento carregado:")

if user_input:
    # Adiciona a pergunta do usuário ao estado da sessão
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Se o usuário pedir para resumir o documento, use o conteúdo do documento como entrada
    if "resumir" in user_input.lower() and 'document_content' in st.session_state:
        user_input = st.session_state['document_content']
    
    # Prepara as mensagens para a API
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
    
    # Chama a API da OpenAI para obter a resposta
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    # Obtém a resposta da API
    assistant_response = response.choices[0].message['content']
    
    # Adiciona a resposta do assistente ao estado da sessão
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
