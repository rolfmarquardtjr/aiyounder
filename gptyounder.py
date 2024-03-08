import streamlit as st
import pandas as pd
import docx
import fitz  # PyMuPDF
from openai import OpenAI

# Inicialização da sessão
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Função para processar o arquivo carregado
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

st.title("💬Chatbot da Younder")

with st.sidebar:
    openai_api_key = st.text_input("Chave da API da OpenAI", key="chatbot_api_key", type="password")
    st.markdown("[Obtenha uma chave da API da OpenAI](https://platform.openai.com/account/api-keys)")
    st.markdown("[Veja o código fonte](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)")

# UI para upload de documentos
file_types = ["PDF", "Excel", "Word"]
file_type = st.selectbox("Tipo de Documento", ["Escolher"] + file_types)
uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
if uploaded_file and file_type != "Escolher":
    document_text = process_file(uploaded_file, file_type)
    st.write("Documento carregado com sucesso!")

    if openai_api_key:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": document_text}])
        msg = response.choices.append({"role": "assistant", "content": msg})
        st.write("Resumo do documento:")
        st.write(msg)
    else:
        st.warning("Por favor, adicione sua chave da API da OpenAI para ver o resumo do documento.")

# Entrada de texto do usuário
prompt = st.text_input("Digite sua pergunta:")
if prompt:
    if openai_api_key:
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        msg = response.choices[0].message.content
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.write("Você perguntou: ", prompt)
        st.write("Resposta do chatbot:")
        st.write(msg)
    else:
        st.warning("Por favor, adicione sua chave da API da OpenAI para continuar o chat.")
