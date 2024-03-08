import streamlit as st
import pandas as pd
import docx
import fitz  # PyMuPDF

# Assumindo que você está planejando usar o OpenAI, mas o import estava errado ou incompleto.
# "from openai import OpenAI" para "import openai" é mais apropriado para uso geral.
import openai

# Funções de processamento de arquivos
def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file) as doc:
        return " ".join(page.get_text() for page in doc)

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return '\n'.join(para.text for para in doc.paragraphs)

def extract_text_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df.to_string(index=False)

def process_file(uploaded_file):
    """Processa o arquivo carregado e retorna seu texto."""
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return extract_text_from_excel(uploaded_file)

# Função de resumo de documento
def summarize_document(api_key, document_text):
    openai.api_key = api_key
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=f"resumo: {document_text}",
      temperature=0.3,
      max_tokens=150,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    st.write(response.choices[0].text.strip())

# Conversação com OpenAI
def converse_with_openai(api_key, prompt):
    openai.api_key = api_key
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      temperature=0.9,
      max_tokens=150,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    st.write(response.choices[0].text.strip())

# UI
def main():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Como posso ajudá-lo?"}]
    if "document_content" not in st.session_state:
        st.session_state["document_content"] = ""

    st.title("💬 Chatbot com Resumo de Documentos")

    with st.sidebar:
        openai_api_key = st.text_input("Chave da API da OpenAI", type="password")
        uploaded_file = st.file_uploader("Carregar documento para resumo", type=["pdf", "xlsx", "docx"])
        if uploaded_file is not None:
            st.session_state["document_content"] = process_file(uploaded_file)

    prompt = st.text_input("Digite sua pergunta ou 'resumir documento':")

    if st.button("Enviar") and prompt and openai_api_key:
        if prompt.lower() == "resumir documento" and st.session_state["document_content"]:
            summarize_document(openai_api_key, st.session_state["document_content"])
        else:
            converse_with_openai(openai_api_key, prompt)

if __name__ == "__main__":
    main()
