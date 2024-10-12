import streamlit as st
import requests
import docx
from io import BytesIO

st.title("Corrector de Ortografía y Gramática")

# Leer la clave de API desde los secrets de Streamlit
API_KEY = st.secrets["together_api_key"]

# Widget para subir el archivo
uploaded_file = st.file_uploader("Sube un documento de Word", type=["docx"])

if uploaded_file is not None:
    # Leer el documento de Word
    document = docx.Document(uploaded_file)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    text = '\n'.join(full_text)
    
    st.write("Documento Original:")
    st.write(text)
    
    # Preparar la solicitud a la API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": f"Corrige la ortografía y la gramática del siguiente texto:\n\n{text}"}],
        "max_tokens": 2512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": False
    }
    
    # Enviar la solicitud a la API de Together
    response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        corrected_text = result["choices"][0]["message"]["content"]
        
        st.write("Documento Corregido:")
        st.write(corrected_text)
        
        # Crear un nuevo documento de Word con el texto corregido
        corrected_document = docx.Document()
        for para in corrected_text.split('\n'):
            corrected_document.add_paragraph(para)
        
        # Guardar en un objeto BytesIO
        corrected_io = BytesIO()
        corrected_document.save(corrected_io)
        corrected_io.seek(0)
        
        # Botón para descargar el documento corregido
        st.download_button(
            label="Descargar Documento Corregido",
            data=corrected_io,
            file_name="documento_corregido.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.error("Error en la solicitud a la API")
        st.error(response.text)
