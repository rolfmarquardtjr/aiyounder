import streamlit as st
import openai
import pandas as pd
import docx
import fitz  # PyMuPDF

# Defina sua chave de API da OpenAI
openai.api_key = "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"

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
    if st.session_state['user_input']:
        message_text = st.session_state['user_input']
        st.session_state.messages.append(f"Você: {message_text}")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": st.session_state['document_content']},
                          {"role": "user", "content": message_text}]
            )
            st.session_state.messages.append(f"Assistente: {response.choices[0].message['content']}")
        except Exception as e:
            st.session_state.messages.append(f"Assistente: Erro ao consultar a OpenAI: {e}")
        st.session_state['user_input'] = ''
        # Dispara a rolagem para baixo após enviar a mensagem
        st.session_state.should_scroll = True

# Inicialize as variáveis de estado da sessão
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ''
if 'document_content' not in st.session_state:
    st.session_state['document_content'] = ''
if 'file_type' not in st.session_state:
    st.session_state['file_type'] = ''
if 'should_scroll' not in st.session_state:
    st.session_state['should_scroll'] = False

# Sidebar para upload de documentos
with st.sidebar:
    st.header("Upload de Documentos")
    file_types = ["PDF", "Excel", "Word"]
    file_type = st.selectbox("Tipo de Documento", options=[""] + file_types)
    if file_type:
        uploaded_file = st.file_uploader("Carregue um arquivo", type=["pdf", "xlsx", "docx"])
        if uploaded_file:
            st.session_state['document_content'] = process_file(uploaded_file, file_type)
            st.text_area("Prévia do documento:", st.session_state['document_content'], height=150)

# Área de chat principal
st.write("Chat")
# Cria um container para o histórico do chat com borda
chat_history_container = st.container()
chat_container_key = "chat_history_container"
with chat_history_container:
    chat_html = f"<div id='{chat_container_key}' style='border:2px solid #4CAF50; padding:10px; overflow-y: auto; height: 400px;'>"
    for message in st.session_state.messages:
        chat_html += f"<div style='margin: 5px 0;'>{message}</div>"
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

# Campo de entrada para o chat
user_input = st.text_input("Digite sua mensagem e pressione Enter:",
              key="user_input",
              on_change=send_message)

# Verifica se deve rolar para baixo
if st.session_state.should_scroll:
    st.session_state.should_scroll = False
    st.markdown(f"""
        <script>
            const chatBox = document.getElementById('{chat_container_key}');
            chatBox.scrollTop = chatBox.scrollHeight;
        </script>
    """, unsafe_allow_html=True)

# Rola automaticamente para a parte inferior do chat a cada nova mensagem
# Removemos o código anterior de rolagem automática
