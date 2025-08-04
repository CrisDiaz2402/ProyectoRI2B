def cargar_ground_truth(consulta):
    """
    Busca el ground truth para la consulta dada en un archivo groundtruth.json.
    El archivo debe tener formato: {"consulta1": ["id1", "id2"], ...}
    """
    ruta = os.path.join(os.path.dirname(__file__), '../data/processed/feedback/groundtruth.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            gt_dict = json.load(f)
        # Busca por consulta exacta (puedes mejorar con normalización o similaridad)
        return gt_dict.get(consulta, [])
    return []

def guardar_resultado_busqueda(retrieved, consulta=None):
    """
    Guarda los resultados de la búsqueda y el ground truth (si existe) en un archivo JSON para evaluación.
    retrieved: lista de nombres/IDs recuperados
    consulta: texto de la consulta (opcional, para buscar ground truth)
    """
    relevant = cargar_ground_truth(consulta) if consulta else []
    ruta = os.path.join(os.path.dirname(__file__), '../data/processed/feedback/resultados_groundtruth.json')
    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    if os.path.exists(ruta):
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            data = []
    else:
        data = []
    data.append({"retrieved": retrieved, "relevant": relevant, "consulta": consulta})
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
import json
import streamlit as st
from PIL import Image
from app.vectorizer import vectorize_text, vectorize_image
from app.utils import buscar_similares, get_original_path, clasificar_resultados_por_tipo
from langdetect import detect
from deep_translator import GoogleTranslator
from app.feedback import registrar_interaccion, registrar_estrellas, obtener_feedback, eliminar_interaccion
import os

def mostrar_resultado(nombre_vector):
    ruta = get_original_path(nombre_vector)
    if not ruta or not os.path.exists(ruta):
        st.warning(f"No se encontró el archivo original para: {nombre_vector}")
        return

    registrar_interaccion(nombre_vector, "clic")
    ruta = ruta.replace("\\", "/")
    st.markdown(f"🔗 **Archivo original:** {ruta}")

    if ruta.endswith((".jpg", ".jpeg", ".png")):
        st.image(Image.open(ruta), caption=nombre_vector, use_column_width=True)
    elif ruta.endswith(".txt"):
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        st.markdown(f"**Texto encontrado:**\n\n\n{contenido}\n")
    elif ruta.endswith((".mp4", ".webm")):
        st.video(ruta)
    elif ruta.endswith((".mp3", ".wav")):
        st.audio(ruta)
    else:
        st.info(f"Archivo multimedia detectado pero no se puede visualizar directamente: {ruta}")


    # 💬 Feedback (solo una vez, sin forms)
    feedback_key = f"feedback_{nombre_vector}"
    if feedback_key not in st.session_state:
        st.session_state[feedback_key] = obtener_feedback(nombre_vector)
    feedback = st.session_state[feedback_key]

    col1, col1b, col2, col2b, col3, col4 = st.columns([2, 1, 2, 1, 3, 2])

    # Like
    with col1:
        if st.button(f"👍 Like ({feedback['likes']})", key=f"like_{nombre_vector}"):
            registrar_interaccion(nombre_vector, "like")
            feedback["likes"] += 1
            st.session_state[feedback_key] = feedback.copy()
            st.success("¡Gracias por tu like!")

    # Eliminar Like
    with col1b:
        if st.button("🗑️", key=f"del_like_{nombre_vector}"):
            eliminar_interaccion(nombre_vector, "like")
            if feedback["likes"] > 0:
                feedback["likes"] -= 1
            st.session_state[feedback_key] = feedback.copy()
            st.info("Like eliminado.")

    # Dislike
    with col2:
        if st.button(f"👎 Dislike ({feedback['dislikes']})", key=f"dislike_{nombre_vector}"):
            registrar_interaccion(nombre_vector, "dislike")
            registrar_estrellas(nombre_vector, 1)
            feedback["dislikes"] += 1
            st.session_state[feedback_key] = feedback.copy()
            st.warning("Dislike registrado.")

    # Eliminar Dislike
    with col2b:
        if st.button("🗑️", key=f"del_dislike_{nombre_vector}"):
            eliminar_interaccion(nombre_vector, "dislike")
            if feedback["dislikes"] > 0:
                feedback["dislikes"] -= 1
            st.session_state[feedback_key] = feedback.copy()
            st.info("Dislike eliminado.")

    # Estrellas
    with col3:
        if feedback["promedio_estrellas"] is not None:
            st.write(f"⭐ Promedio: {feedback['promedio_estrellas']} ({feedback['num_estrellas']} votos)")
        estrellas = st.slider("Califica este resultado:", 1, 5, 3, key=f"slider_{nombre_vector}")
    with col4:
        if st.button("Enviar calificación", key=f"rate_{nombre_vector}"):
            registrar_estrellas(nombre_vector, estrellas)
            feedback = obtener_feedback(nombre_vector)
            st.session_state[feedback_key] = feedback.copy()
            st.success("¡Gracias por tu calificación!")

    # Fin feedback simplificado

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

    # Inicializar session_state para resultados y tipo
    if 'resultados_busqueda' not in st.session_state:
        st.session_state['resultados_busqueda'] = None
    if 'agrupados_busqueda' not in st.session_state:
        st.session_state['agrupados_busqueda'] = None
    if 'tipo_busqueda' not in st.session_state:
        st.session_state['tipo_busqueda'] = None
    if 'consulta_actual' not in st.session_state:
        st.session_state['consulta_actual'] = ''

    mostrar_resultados = False

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
                    st.info(f"🔄 Consulta traducida automáticamente de **{idioma}** → **en**: {consulta_traducida}")
                except Exception as e:
                    st.warning("No se pudo traducir la consulta automáticamente. Se usará el texto original.")
                    consulta_traducida = consulta
            else:
                consulta_traducida = consulta

            vector = vectorize_text(consulta_traducida)
            resultados = buscar_similares(vector, "data/processed/embeddings", top_k=20)
            agrupados = clasificar_resultados_por_tipo(resultados)

            st.session_state['resultados_busqueda'] = resultados
            st.session_state['agrupados_busqueda'] = agrupados
            st.session_state['tipo_busqueda'] = 'Texto'
            st.session_state['consulta_actual'] = consulta
            mostrar_resultados = True

            # Guardar resultados para evaluación automática
            nombres_resultados = [nombre for nombre, _ in resultados]
            # Si tienes ground truth para la consulta, ponlo aquí. Si no, se guarda vacío.
            guardar_resultado_busqueda(nombres_resultados, consulta=consulta)
        elif st.session_state['resultados_busqueda'] is not None and st.session_state['tipo_busqueda'] == 'Texto':
            agrupados = st.session_state['agrupados_busqueda']
            mostrar_resultados = True

    else:
        imagen = st.file_uploader("Sube una imagen para buscar contenido relacionado", type=["jpg", "jpeg", "png"])
        if imagen:
            st.image(Image.open(imagen), caption="Imagen cargada", use_column_width=True)

            if st.button("🔎 Buscar"):
                vector = vectorize_image(imagen)
                resultados = buscar_similares(vector, "data/processed/embeddings", top_k=20)
                agrupados = clasificar_resultados_por_tipo(resultados)

                st.session_state['resultados_busqueda'] = resultados
                st.session_state['agrupados_busqueda'] = agrupados
                st.session_state['tipo_busqueda'] = 'Imagen'
                st.session_state['consulta_actual'] = ''
                mostrar_resultados = True

                # Guardar resultados para evaluación automática
                nombres_resultados = [nombre for nombre, _ in resultados]
                guardar_resultado_busqueda(nombres_resultados, consulta=None)
            elif st.session_state['resultados_busqueda'] is not None and st.session_state['tipo_busqueda'] == 'Imagen':
                agrupados = st.session_state['agrupados_busqueda']
                mostrar_resultados = True

    if mostrar_resultados:
        for tipo, grupo in st.session_state['agrupados_busqueda'].items():
            if grupo:
                st.subheader(f"📂 Resultados: {tipo.upper()}")
                for nombre, score in grupo:
                    st.markdown(f"{score:.3f} — **{nombre}**")
                    mostrar_resultado(nombre)

    st.markdown('</div>', unsafe_allow_html=True)