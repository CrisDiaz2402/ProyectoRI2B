# main.py


import streamlit as st
from app import buscador, feedback, evaluacion


st.set_page_config(
    page_title="Buscador Multimodal Inteligente",
    page_icon="🔍",
    layout="wide"
)

# Estilo personalizado para la página y barra lateral
st.markdown(
    """
    <style>
        .main-title {
            font-size: 40px;
            font-weight: 800;
            color: #4A90E2;
            margin-bottom: 10px;
        }
        .sub-title {
            font-size: 20px;
            color: #5A5A5A;
            margin-top: -10px;
            margin-bottom: 30px;
        }
        .sidebar .sidebar-content {
            background-color: #f5f5f5;
        }
        .css-1v3fvcr {
            background-color: #f5f5f5 !important;
        }
        section[data-testid="stSidebar"] button.stButton {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            height: 50px !important;
            margin-bottom: 12px;
            border-radius: 12px;
            font-size: 17px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
        }
        section[data-testid="stSidebar"] button.stButton > div {
            width: 100%;
            min-width: 100%;
            max-width: 100%;
            text-align: center;
            box-sizing: border-box;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Encabezado con columnas y estilo
col1, col2 = st.columns([6,1])
with col1:
    st.markdown('<div class="main-title">🔍 Buscador Multimodal Inteligente</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Consulta por texto, imagen o audio y obtén resultados relacionados</div>', unsafe_allow_html=True)
with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=90)


# Menú de navegación lateral con botones y estilo
st.sidebar.title("� Navegación Principal")
st.sidebar.markdown("---")

secciones = [
    ("🔎 Buscador Multimodal", buscador.mostrar_buscador),
    ("📊 Evaluación del Sistema", evaluacion.mostrar_metricas),
    ("⭐ Feedback del Usuario", feedback.mostrar_feedback)
]

if "seccion_seleccionada" not in st.session_state:
    st.session_state["seccion_seleccionada"] = secciones[0][0]

for nombre, _ in secciones:
    if st.sidebar.button(nombre, key=nombre):
        st.session_state["seccion_seleccionada"] = nombre

for nombre, funcion in secciones:
    if st.session_state["seccion_seleccionada"] == nombre:
        funcion()
        break

# Footer
st.markdown("---")
st.markdown(
    "<center><small>© 2025 Buscador Multimodal Inteligente · Todos los derechos reservados</small></center>",
    unsafe_allow_html=True
)
