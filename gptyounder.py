import streamlit as st
import pandas as pd
import docx
import fitz  # PyMuPDF
from openai import OpenAI

# Solicita a chave da API da OpenAI através da interface do Streamlit
with st.sidebar:
    openai_api_key = st.text_input("Chave da API da OpenAI", "chatbot_api_key", type="password")
    st.markdown("[Obtenha uma chave da API da OpenAI](https://platform.openai.com/account/api-keys)")

    # UI para upload de documentos
    st.header("Upload de Documentos")
    file_types = ["PDF", "Excel", "Word"]
    file_type = st.selectbox("Tipo de Documento", ["Escolher"] + file_types)
    uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
    if uploaded_file and file_type != "Escolher":
        process_and_summarize_file(uploaded_file, file_type)

# Adicionando o logo e título
st.image("https://younder.com.br/wp-content/uploads/2023/03/Logotipo-Younder-horizontal-principal-1-1024x447.png", width=300)
st.title("💬 Chatbot da Younder")

# Função para processamento e solicitação de resumo do arquivo
def process_and_summarize_file(uploaded_file, file_type):
    """Processa e solicita um resumo para o arquivo carregado."""
    document_content = process_file(uploaded_file, file_type)
    if not openai_api_key:
        st.info("Por favor, adicione sua chave da API da OpenAI para continuar.")
        return
    # Inicializa o cliente da OpenAI
    client = OpenAI(api_key=openai_api_key)
    # Solicita resumo
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": f"Resuma o seguinte texto: {document_content}"}])
    msg = response.choices[0].message.content
    # Exibe o resumo
    st.session_state["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

# Reutilizamos a função process_file original para extração de texto do arquivo
def process_file(uploaded_file, file_type):
    """Extrai texto de arquivos PDF, Excel, Word."""
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

# A lógica de interação do chatbot permanece a mesma
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "Como posso ajudá-lo?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Entrada de texto do usuário
if prompt := st.chat_input("Digite sua pergunta"):
    handle_user_input(prompt)
