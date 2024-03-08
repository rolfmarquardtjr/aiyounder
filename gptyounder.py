import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF

# Acessar a chave da API da OpenAI de forma segura
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

openai.api_key = OPENAI_API_KEY

def process_file(uploaded_file, file_type):
    """Processa arquivos PDF, Excel ou Word e retorna o texto."""
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

def send_message(user_input):
    """Envia a mensagem do usuário para a API da OpenAI e registra a resposta."""
    if user_input:
        document_content = st.session_state.get('document_content', '')
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": document_content},
                          {"role": "user", "content": user_input}]
            )
            response_text = response.choices[0].message['content']
            st.session_state.messages.append(f"Você: {user_input}")
            st.session_state.messages.append(f"Assistente: {response_text}")
        except Exception as e:
            st.session_state.messages.append(f"Assistente: Erro ao consultar a OpenAI: {str(e)}")

# Inicializar o estado da sessão
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Interface do usuário para upload de documentos
with st.sidebar:
    st.header("Upload de Documentos")
    file_types = ["PDF", "Excel", "Word"]
    file_type = st.selectbox("Tipo de Documento", ["Escolher"] + file_types)
    if file_type != "Escolher":
        uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
        if uploaded_file:
            document_content = process_file(uploaded_file, file_type)
            st.session_state['document_content'] = document_content
            st.text_area("Prévia do documento:", value=document_content[:500] + "...", height=150, disabled=True)

# Interface do usuário para o chat
st.title("Chat com ChatGPT")
user_input = st.text_input("Digite sua mensagem:", key="user_input")

if st.button("Enviar") and user_input:
    send_message(user_input)
    st.session_state['user_input'] = ''  # Limpar o campo após enviar

# Exibir o histórico de mensagens
for message in st.session_state['messages']:
    st.text(message)

# Implementação da rolagem automática não é necessária aqui, pois o Streamlit cuida do scroll
