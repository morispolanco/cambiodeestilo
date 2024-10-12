import streamlit as st
import requests
import docx
from io import BytesIO

def main():
    st.title("Cambiar estilo de documento Word")
    
    uploaded_file = st.file_uploader("Sube un documento Word", type=["docx"])
    
    if uploaded_file is not None:
        doc = docx.Document(uploaded_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        text = '\n'.join(full_text)
        
        st.write("Texto original:")
        st.text_area("", text, height=200)
        
        # Procesar el texto usando la API de Together
        if st.button("Cambiar estilo"):
            modified_text = change_style_with_together_api(text)
            if modified_text:
                st.write("Texto modificado:")
                st.text_area("", modified_text, height=200)
            else:
                st.error("No se pudo modificar el texto.")

def change_style_with_together_api(text):
    api_key = st.secrets["together_api_key"]
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "user", "content": f"Cambia el estilo del siguiente texto:\n\n{text}"}
        ],
        "max_tokens": 2512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1.0,
        "stop": ["<|eot_id|>"],
        "stream": False
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        # Extraer la respuesta del asistente
        try:
            modified_text = result['choices'][0]['message']['content']
            return modified_text
        except (KeyError, IndexError):
            st.error("Error en el formato de la respuesta de la API.")
            return ""
    else:
        st.error(f"Error en la llamada a la API: {response.status_code}")
        return ""

if __name__ == "__main__":
    main()
