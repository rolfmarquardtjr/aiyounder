import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF

# Defina sua chave de API da OpenAI
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# Inicializa as variáveis de estado
st.session_state.setdefault('messages', [])
st.session_state.setdefault('user_input', '')

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

def send_message(user_input, document_content=""):
    """Envia a mensagem do usuário para a OpenAI e retorna a resposta."""
    if not user_input:
        return ""

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    if document_content:  # Inclui o conteúdo do documento como contexto se disponível
        messages.append({"role": "system", "content": document_content})
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message['content']

# Adicionando o logo e configurando a interface do usuário
st.sidebar.image("https://younder.com.br/wp-content/uploads/2023/03/Logotipo-Younder-horizontal-principal-1-1024x447.png", width=300)
st.sidebar.header("Upload de Documentos (Opcional)")
file_type = st.sidebar.selectbox("Tipo de Documento", ["Nenhum", "PDF", "Excel", "Word"])
document_content = ""
if file_type != "Nenhum":
    uploaded_file = st.sidebar.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
    if uploaded_file:
        document_content = process_file(uploaded_file, file_type)
        st.sidebar.text_area("Prévia do documento", value=document_content[:500] + "...", height=150)

st.title("Chat com ChatGPT")
user_input = st.text_input("Digite sua pergunta relacionada ao documento:", key="input", value=st.session_state['user_input'])

# Botão de envio
if st.button("Enviar"):
    response = send_message(user_input, document_content)
    st.session_state['messages'].append(f"Você: {user_input}")
    st.session_state['messages'].append(f"Assistente: {response}")
    # Limpa o campo de entrada
    st.session_state['user_input'] = ""
