# app/search.py
import streamlit as st
from PIL import Image
import numpy as np
import os
from app.vectorizer import vectorize_text, vectorize_image
from app.utils import buscar_similares

def mostrar_resultado(nombre_vector):
    base_dirs = {
        "frames": "data/processed/frames",
        "images_crawled": "data/raw/crawled",
        "images_flickr": "data/raw/flickr",
        "texts": "data/processed/transcripts",
        "texts_raw": "data/raw/texto"
    }

    if nombre_vector.startswith("video"):
        # Buscar imagen de frame
        partes = nombre_vector.split("_")
        video = partes[0]
        frame = "_".join(partes[1:])
        for carpeta in os.listdir(base_dirs["frames"]):
            frame_path = os.path.join(base_dirs["frames"], carpeta, frame + ".jpg")
            if os.path.exists(frame_path):
                st.image(Image.open(frame_path), caption=nombre_vector)
                return

    elif nombre_vector.startswith("gatos") or nombre_vector.startswith("images_crawled"):
        nombre_archivo = nombre_vector + ".jpg"
        path = os.path.join(base_dirs["images_crawled"], nombre_archivo)
        if os.path.exists(path):
            st.image(Image.open(path), caption=nombre_vector)
            return

    elif nombre_vector.startswith("100") or "flickr" in nombre_vector:
        nombre_archivo = nombre_vector + ".jpg"
        path = os.path.join(base_dirs["images_flickr"], nombre_archivo)
        if os.path.exists(path):
            st.image(Image.open(path), caption=nombre_vector)
            return

    elif os.path.exists(os.path.join(base_dirs["texts"], nombre_vector + ".txt")):
        path = os.path.join(base_dirs["texts"], nombre_vector + ".txt")
        with open(path, "r", encoding="utf-8") as f:
            contenido = f.read()
        st.markdown(f"**Texto encontrado:**\n\n{contenido}")
        return

    elif os.path.exists(os.path.join(base_dirs["texts_raw"], nombre_vector + ".txt")):
        path = os.path.join(base_dirs["texts_raw"], nombre_vector + ".txt")
        with open(path, "r", encoding="utf-8") as f:
            contenido = f.read()
        st.markdown(f"**Texto encontrado:**\n\n{contenido}")
        return

    st.warning(f"No se puede mostrar el resultado: {nombre_vector}")

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
            vector = vectorize_text(consulta)
            resultados = buscar_similares(vector, "data/processed/embeddings", top_k=10)
            st.success("Resultados similares:")
            for nombre, score in resultados:
                st.markdown(f"📂 **{nombre}** — Similaridad: {score:.3f}")
                mostrar_resultado(nombre)

    else:
        imagen = st.file_uploader("Sube una imagen para buscar contenido relacionado", type=["jpg", "jpeg", "png"])
        if imagen:
            st.image(Image.open(imagen), caption="Imagen cargada", use_column_width=True)
            if st.button("🔎 Buscar"):
                vector = vectorize_image(imagen)
                resultados = buscar_similares(vector, "data/processed/embeddings", top_k=10)
                st.success("Resultados similares:")
                for nombre, score in resultados:
                    st.markdown(f"📂 **{nombre}** — Similaridad: {score:.3f}")
                    mostrar_resultado(nombre)

    st.markdown('</div>', unsafe_allow_html=True)