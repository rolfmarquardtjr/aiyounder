import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF

# Acessa a chave da API da OpenAI dos Secrets do Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

def process_file(uploaded_file, file_type):
    """Processa o arquivo carregado com base em seu tipo e retorna seu texto."""
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

def send_message(user_input, document_content):
    """Envia a mensagem do usuário e o conteúdo do documento para a API da OpenAI e retorna a resposta."""
    if user_input:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": document_content},
                      {"role": "user", "content": user_input}]
        )
        return response.choices[0].message['content']

# Inicialização das variáveis de estado da sessão
if 'messages' not in st.session_state:
    st.session_state.messages = []

# UI para upload de documentos
with st.sidebar:
    st.header("Upload de Documentos")
    file_type = st.selectbox("Tipo de Documento", ["PDF", "Excel", "Word"])
    document_content = ""
    if file_type != "Escolher":
        uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
        if uploaded_file:
            document_content = process_file(uploaded_file, file_type)
            st.session_state.document_content = document_content
            st.text_area("Prévia do documento:", value=document_content[:500] + "...", height=150, disabled=True)

# UI para o chat
st.title("Chat com ChatGPT")
user_input = st.text_input("Digite sua mensagem:", key="user_input")

if st.button("Enviar") and user_input:
    assistant_response = send_message(user_input, st.session_state.get('document_content', ''))
    st.session_state.messages.append(f"Você: {user_input}")
    st.session_state.messages.append(f"Assistente: {assistant_response}")
    st.session_state.user_input = ''  # Limpa o input após enviar

# Exibe o chat em um container com rolagem automática
st.write("Conversa:")
for message in st.session_state.messages:
    sender, msg = message.split(":", 1)
    st.text_area(label=sender, value=msg, height=75, disabled=True)

# Implementar rolagem automática se necessário
