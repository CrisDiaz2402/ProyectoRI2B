import json
import os
import streamlit as st
from PIL import Image
from app.vectorizer import vectorize_text, vectorize_image
from app.utils import buscar_similares, get_original_path, clasificar_resultados_por_tipo
from langdetect import detect
from deep_translator import GoogleTranslator
from app.feedback import registrar_interaccion, registrar_estrellas, obtener_feedback, eliminar_interaccion

# --- Función para guardar resultados + ground truth manual ---
def guardar_resultado_manual(retrieved, relevant, consulta):
    ruta = os.path.join(os.path.dirname(__file__), '../data/processed/feedback/resultados_groundtruth.json')
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    if os.path.exists(ruta):
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            data = []
    else:
        data = []

    data.append({
        "retrieved": retrieved,
        "relevant": relevant,
        "consulta": consulta
    })

    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Mostrar resultado multimedia ---
def mostrar_resultado(nombre_vector, meta):
    # meta puede ser None si no se encontró en metadata
    if not meta or 'path' not in meta or not meta['path']:
        st.warning(f"No se encontró el archivo original para: {nombre_vector}")
        return

    ruta = meta['path']
    if not isinstance(ruta, str):
        st.warning(f"Ruta inválida para: {nombre_vector}")
        return
    if not os.path.exists(ruta):
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

    # Feedback simplificado (igual que antes)
    feedback_key = f"feedback_{nombre_vector}"
    if feedback_key not in st.session_state:
        st.session_state[feedback_key] = obtener_feedback(nombre_vector)
    feedback = st.session_state[feedback_key]

    col1, col1b, col2, col2b, col3, col4 = st.columns([2, 1, 2, 1, 3, 2])

    with col1:
        if st.button(f"👍 Like ({feedback['likes']})", key=f"like_{nombre_vector}"):
            registrar_interaccion(nombre_vector, "like")
            feedback["likes"] += 1
            st.session_state[feedback_key] = feedback.copy()
            st.success("¡Gracias por tu like!")

    with col1b:
        if st.button("🗑️", key=f"del_like_{nombre_vector}"):
            eliminar_interaccion(nombre_vector, "like")
            if feedback["likes"] > 0:
                feedback["likes"] -= 1
            st.session_state[feedback_key] = feedback.copy()
            st.info("Like eliminado.")

    with col2:
        if st.button(f"👎 Dislike ({feedback['dislikes']})", key=f"dislike_{nombre_vector}"):
            registrar_interaccion(nombre_vector, "dislike")
            registrar_estrellas(nombre_vector, 1)
            feedback["dislikes"] += 1
            st.session_state[feedback_key] = feedback.copy()
            st.warning("Dislike registrado.")

    with col2b:
        if st.button("🗑️", key=f"del_dislike_{nombre_vector}"):
            eliminar_interaccion(nombre_vector, "dislike")
            if feedback["dislikes"] > 0:
                feedback["dislikes"] -= 1
            st.session_state[feedback_key] = feedback.copy()
            st.info("Dislike eliminado.")

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

# --- Página principal de búsqueda ---
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
                except Exception:
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

        elif st.session_state['resultados_busqueda'] is not None and st.session_state['tipo_busqueda'] == 'Texto':
            agrupados = st.session_state['agrupados_busqueda']
            mostrar_resultados = True

    else:
        imagen = st.file_uploader("Sube una imagen para buscar contenido relacionado", type=["jpg", "jpeg", "png"])
        if imagen:
            st.image(Image.open(imagen), caption="Imagen cargada", use_column_width=True)
            descripcion = st.text_input("Describe esta imagen para la evaluación (obligatorio)", key="desc_imagen")

            buscar_key = f"buscar_imagen_{descripcion.strip()}"
            if st.button("🔎 Buscar", key=buscar_key):
                if descripcion.strip():
                    vector = vectorize_image(imagen)
                    # Calcular histograma de la imagen de consulta
                    from app.utils import calcular_histograma_imagen
                    histograma = calcular_histograma_imagen(imagen)
                    resultados = buscar_similares(vector, "data/processed/embeddings", top_k=20, histograma_consulta=histograma)
                    agrupados = clasificar_resultados_por_tipo(resultados)

                    st.session_state['resultados_busqueda'] = resultados
                    st.session_state['agrupados_busqueda'] = agrupados
                    st.session_state['tipo_busqueda'] = 'Imagen'
                    st.session_state['consulta_actual'] = descripcion
                    mostrar_resultados = True
                else:
                    st.warning("Por favor, ingresa una descripción para la imagen para continuar.")
        elif st.session_state['resultados_busqueda'] is not None and st.session_state['tipo_busqueda'] == 'Imagen':
            agrupados = st.session_state['agrupados_busqueda']
            mostrar_resultados = True

    # Mostrar resultados y formulario de relevancia manual
    if mostrar_resultados:
        for tipo, grupo in st.session_state['agrupados_busqueda'].items():
            if grupo:
                st.subheader(f"📂 Resultados: {tipo.upper()}")
                relevantes_usuario = []

                for nombre, score, meta in grupo:
                    # Mostrar detalles enriquecidos de la metadata si existen
                    detalles = meta.get("detalles", "") if meta else ""
                    bonus = meta.get("bonus_feedback", 0.0) if meta else 0.0
                    feedback_key = meta.get("feedback_key", nombre) if meta else nombre
                    st.markdown(f"{score:.3f} — **{nombre}**  ")
                    st.caption(f"Bonus feedback: {bonus:.3f} | Feedback key usada: {feedback_key}")
                    if detalles:
                        st.info(f"**Detalles metadata:** {detalles}")
                    mostrar_resultado(nombre, meta)
                    marcado = st.checkbox(f"Marcar como relevante: {nombre}", key=f"relevante_{nombre}")
                    if marcado:
                        relevantes_usuario.append(nombre)

                boton_key = f"guardar_gt_{tipo}_{st.session_state['consulta_actual'] or tipo}"
                if st.button(f"Guardar ground truth para consulta '{st.session_state['consulta_actual'] or tipo}'", key=boton_key):
                    retrieved = [nombre for nombre, score, meta in grupo]
                    relevant = relevantes_usuario
                    consulta = st.session_state['consulta_actual'] or "manual_" + tipo
                    guardar_resultado_manual(retrieved, relevant, consulta)
                    st.success("Ground truth guardado correctamente.")

    st.markdown('</div>', unsafe_allow_html=True)