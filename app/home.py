# app/home.py
import streamlit as st

def pagina_inicio():
    st.title("🔎 Plataforma de Recuperación Multimedia Multiformato")
    st.markdown("""
    Bienvenido a la demo del sistema de recuperación de información multimodal.  
    Esta plataforma permite realizar búsquedas por texto o imagen, y encuentra contenido relacionado en videos, imágenes y audios previamente procesados.

    ---
    ### 🧠 Funcionalidades principales
    - 🔤 Consulta por texto e imágenes
    - 🎥 Procesamiento automático de video y audio
    - 🧬 Vectorización con modelos CLIP / BLIP
    - 📊 Evaluación de precisión y feedback del usuario

    ---
    ### 📂 Navegación
    Usa el menú lateral para:
    - Realizar búsquedas
    - Evaluar resultados
    - Enviar comentarios o feedback
    """)