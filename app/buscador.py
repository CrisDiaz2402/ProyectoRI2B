def mostrar_buscador():
    import streamlit as st
    from PIL import Image

    st.markdown(
        """
        <style>
        .centered-input .stTextInput > div > div > input {
            text-align: center;
        }
        .centered-title {
            text-align: center;
            font-size: 30px;
        }
        .centered-sub {
            text-align: center;
            font-size: 18px;
            color: gray;
            margin-bottom: 20px;
        }
        .custom-button {
            display: flex;
            justify-content: center;
            gap: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Título central
    st.markdown('<h1 class="centered-title">Buscador Multimodal</h1>', unsafe_allow_html=True)
    st.markdown('<p class="centered-sub">Realiza tu búsqueda por texto o imagen</p>', unsafe_allow_html=True)

    # Zona central de entrada
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        query_text = st.text_input("", placeholder="Escribe tu búsqueda...", key="text_input")

        st.markdown("o")
        uploaded_image = st.file_uploader("Subir una imagen", type=["jpg", "png", "jpeg"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Botón de búsqueda
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        buscar = st.button("🔍 Buscar")

    # Simulación de resultados
    if buscar:
        st.markdown("---")
        st.subheader("📁 Resultados encontrados")

        if query_text:
            st.markdown(f"🔎 Resultados relacionados con el texto: **'{query_text}'**")

        if uploaded_image:
            st.image(Image.open(uploaded_image), caption="Imagen subida", width=250)
            st.markdown("🔍 Resultados relacionados con la imagen proporcionada")

        # Resultados simulados (luego se conectará con lógica de búsqueda real)
        st.info("Aquí se mostrarán imágenes, videos, audios o textos similares...")