import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF

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
def send_message(user_input, document_content, openai_api_key):
    if user_input:
        try:
            openai.api_key = openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": document_content},
                          {"role": "user", "content": user_input}]
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"Erro ao consultar a OpenAI: {str(e)}"

# Sidebar para configuração da chave da API e upload de documentos
with st.sidebar:
    st.header("Configurações")
    openai_api_key = st.text_input("OpenAI API Key", "", type="password")
    file_types = ["Escolher", "PDF", "Excel", "Word"]
    file_type = st.selectbox("Tipo de Documento", options=file_types)
    uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
    document_content = ""
    if uploaded_file and file_type != "Escolher":
        document_content = process_file(uploaded_file, file_type)
        st.text_area("Prévia do documento:", value=document_content[:500] + "...", height=150)

# Inicialização das variáveis de estado da sessão
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Área de chat principal
st.title("Chat com ChatGPT")
user_input = st.text_input("Digite sua mensagem:", "")

# Enviar mensagem e mostrar resposta
if st.button("Enviar") and user_input:
    if openai_api_key:  # Verifica se a chave da API foi fornecida
        assistant_response = send_message(user_input, document_content, openai_api_key)
        st.session_state.messages.append(f"Você: {user_input}")
        st.session_state.messages.append(f"Assistente: {assistant_response}")
    else:
        st.warning("Por favor, insira a chave da API da OpenAI.")

# Exibição do histórico de mensagens
for message in st.session_state.messages:
    st.text(message)
