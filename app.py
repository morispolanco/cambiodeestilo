import streamlit as st
import requests
import docx
from io import BytesIO

def main():
    st.title("Cambiar estilo de documento Word")

    uploaded_file = st.file_uploader("Sube un documento Word", type=["docx"])

    if uploaded_file is not None:
        doc = docx.Document(uploaded_file)
        paragraphs = [para.text for para in doc.paragraphs]

        st.write("Texto original:")
        original_text = '\n'.join(paragraphs)
        st.text_area("", original_text, height=200)

        # Preguntar al usuario a qué estilo quiere cambiar el texto
        desired_style = st.text_input("¿A qué estilo quieres cambiar el texto?")

        # Procesar el texto usando la API de Together
        if st.button("Cambiar estilo"):
            if desired_style:
                # Mostrar barra de progreso
                with st.spinner("Procesando..."):
                    modified_paragraphs = change_style_with_together_api(paragraphs, desired_style)
                if modified_paragraphs:
                    modified_text = '\n'.join(modified_paragraphs)
                    st.write("Texto modificado:")
                    st.text_area("", modified_text, height=200)

                    # Crear un nuevo documento Word con el texto modificado
                    modified_doc = docx.Document()
                    for paragraph in modified_paragraphs:
                        modified_doc.add_paragraph(paragraph)

                    # Guardar el documento en un objeto BytesIO
                    docx_stream = BytesIO()
                    modified_doc.save(docx_stream)
                    docx_stream.seek(0)

                    # Botón para descargar el documento modificado
                    st.download_button(
                        label="Descargar documento modificado",
                        data=docx_stream,
                        file_name="documento_modificado.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("No se pudo modificar el texto.")
            else:
                st.warning("Por favor, especifica a qué estilo quieres cambiar el texto.")

def change_style_with_together_api(paragraphs, desired_style):
    api_key = st.secrets["together_api_key"]
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    modified_paragraphs = []
    total_paragraphs = len(paragraphs)
    progress_bar = st.progress(0)

    for idx, paragraph in enumerate(paragraphs):
        if paragraph.strip() == "":
            # Si el párrafo está vacío, lo añadimos tal cual
            modified_paragraphs.append(paragraph)
            continue

        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [
                {"role": "user", "content": f"Cambia el estilo del siguiente texto al estilo '{desired_style}':\n\n{paragraph}"}
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
            # Extraer la respuesta del asistente
            try:
                modified_paragraph = result['choices'][0]['message']['content'].strip()
                modified_paragraphs.append(modified_paragraph)
            except (KeyError, IndexError):
                st.error("Error en el formato de la respuesta de la API.")
                return None
        else:
            st.error(f"Error en la llamada a la API: {response.status_code}")
            return None

        # Actualizar la barra de progreso
        progress = (idx + 1) / total_paragraphs
        progress_bar.progress(progress)

    return modified_paragraphs

if __name__ == "__main__":
    main()
