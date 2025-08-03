import streamlit as st
from PIL import Image
from app.vectorizer import vectorize_text, vectorize_image
from app.utils import buscar_similares, get_original_path, clasificar_resultados_por_tipo
from langdetect import detect
from deep_translator import GoogleTranslator
import os

def mostrar_resultado(nombre_vector):
    ruta = get_original_path(nombre_vector)

    if not ruta or not os.path.exists(ruta):
        st.warning(f"No se encontró el archivo original para: {nombre_vector}")
        return

    ruta = ruta.replace("\\", "/")
    st.markdown(f"🔗 **Archivo original:** `{ruta}`")

    if ruta.endswith((".jpg", ".jpeg", ".png")):
        st.image(Image.open(ruta), caption=nombre_vector, use_column_width=True)

    elif ruta.endswith(".txt"):
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        st.markdown(f"**Texto encontrado:**\n\n```\n{contenido}\n```")

    elif ruta.endswith((".mp4", ".webm")):
        st.video(ruta)

    elif ruta.endswith((".mp3", ".wav")):
        st.audio(ruta)

    else:
        st.info(f"Archivo multimedia detectado pero no se puede visualizar directamente: `{ruta}`")

def pagina_busqueda():
    st.markdown(
        """
        <style>
            .centered {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin-top: 8%;
            }
            .search-box {
                width: 100%;
                max-width: 600px;
            }
            .submit-button {
                margin-top: 1rem;
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="centered">', unsafe_allow_html=True)

    tipo_busqueda = st.radio("Selecciona el tipo de búsqueda:", ["Texto", "Imagen"], horizontal=True)

    if tipo_busqueda == "Texto":
        consulta = st.text_input("Escribe tu consulta aquí:", key="busqueda_texto")

        if st.button("🔎 Buscar") and consulta:
            try:
                idioma = detect(consulta)
            except:
                idioma = "unknown"

            if idioma != "en":
                try:
                    consulta_traducida = GoogleTranslator(source='auto', target='en').translate(consulta)
                    st.info(f"🔄 Consulta traducida automáticamente de **{idioma}** → **en**: `{consulta_traducida}`")
                except Exception as e:
                    st.warning("No se pudo traducir la consulta automáticamente. Se usará el texto original.")
                    consulta_traducida = consulta
            else:
                consulta_traducida = consulta

            vector = vectorize_text(consulta_traducida)
            resultados = buscar_similares(vector, "data/processed/embeddings", top_k=20)
            agrupados = clasificar_resultados_por_tipo(resultados)

            for tipo, grupo in agrupados.items():
                if grupo:
                    st.subheader(f"📂 Resultados: {tipo.upper()}")
                    for nombre, score in grupo:
                        st.markdown(f"`{score:.3f}` — **{nombre}**")
                        mostrar_resultado(nombre)

    else:
        imagen = st.file_uploader("Sube una imagen para buscar contenido relacionado", type=["jpg", "jpeg", "png"])
        if imagen:
            st.image(Image.open(imagen), caption="Imagen cargada", use_column_width=True)

            if st.button("🔎 Buscar"):
                vector = vectorize_image(imagen)
                resultados = buscar_similares(vector, "data/processed/embeddings", top_k=20)
                agrupados = clasificar_resultados_por_tipo(resultados)

                for tipo, grupo in agrupados.items():
                    if grupo:
                        st.subheader(f"📂 Resultados: {tipo.upper()}")
                        for nombre, score in grupo:
                            st.markdown(f"`{score:.3f}` — **{nombre}**")
                            mostrar_resultado(nombre)

    st.markdown('</div>', unsafe_allow_html=True)