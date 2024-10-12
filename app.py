import streamlit as st
import requests
import docx
from io import BytesIO

def main():
    st.title("Corregir documento Word")

    uploaded_file = st.file_uploader("Sube un documento Word", type=["docx"])

    if uploaded_file is not None:
        doc = docx.Document(uploaded_file)
        paragraphs = [para.text for para in doc.paragraphs]

        st.write("Texto original:")
        original_text = '\n'.join(paragraphs)
        st.text_area("", original_text, height=200)

        if st.button("Corregir texto"):
            with st.spinner("Procesando..."):
                corrected_paragraphs = correct_text_with_together_api(paragraphs)
            if corrected_paragraphs:
                corrected_text = '\n'.join(corrected_paragraphs)
                st.write("Texto corregido:")
                st.text_area("", corrected_text, height=200)

                corrected_doc = docx.Document()
                for paragraph in corrected_paragraphs:
                    corrected_doc.add_paragraph(paragraph)

                docx_stream = BytesIO()
                corrected_doc.save(docx_stream)
                docx_stream.seek(0)

                st.download_button(
                    label="Descargar documento corregido",
                    data=docx_stream,
                    file_name="documento_corregido.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.error("No se pudo corregir el texto.")

def correct_text_with_together_api(paragraphs):
    api_key = st.secrets["together_api_key"]
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    corrected_paragraphs = []
    total_paragraphs = len(paragraphs)
    progress_bar = st.progress(0)

    for idx, paragraph in enumerate(paragraphs):
        if paragraph.strip() == "":
            corrected_paragraphs.append(paragraph)
            continue

        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [
                {"role": "user", "content": f"Corrige el siguiente texto sin añadir explicaciones ni comentarios, solo devuelve el texto corregido:\n\n{paragraph}"}
            ],
            "max_tokens": 2512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stop": ["<|eot_id|>"],
            "stream": False
        }

        try:
            response = requests.post(url, headers=headers, json=data)
        except requests.exceptions.RequestException as e:
            st.error(f"Error de red: {e}")
            return None

        if response.status_code == 200:
            result = response.json()
            try:
                corrected_paragraph = result['choices'][0]['message']['content'].strip()
                corrected_paragraphs.append(corrected_paragraph)
            except (KeyError, IndexError):
                st.error("Error en el formato de la respuesta de la API.")
                return None
        else:
            st.error(f"Error en la llamada a la API: {response.status_code}")
            return None

        progress = (idx + 1) / total_paragraphs
        progress_bar.progress(progress)

    return corrected_paragraphs

if __name__ == "__main__":
    main()
