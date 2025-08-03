# import streamlit as st
# from app import home, search, feedback, evaluation

# PAGES = {
#     "Inicio": home,
#     "Búsqueda": search,
#     "Feedback": feedback,
#     "Evaluación": evaluation
# }

# st.sidebar.title("Navegación")
# page = st.sidebar.radio("Ir a", list(PAGES.keys()))
# PAGES[page].app()  # Cada módulo tiene una función `app()`

# import streamlit as st
# from app.search import run_search  # Función principal de búsqueda multimodal

# def main():
#     st.set_page_config(page_title="Buscador Multimodal", layout="wide")
#     st.title("Buscador Multimodal")
#     run_search()  # Aquí se ejecuta la lógica del buscador

# if __name__ == "__main__":
#     main()

# main.py
import streamlit as st
from app import home, search, feedback, evaluation

st.set_page_config(page_title="Buscador Multimodal", layout="wide")

# Barra lateral de navegación
pagina = st.sidebar.selectbox("📂 Navegación", [
    "Inicio",
    "Búsqueda Multimodal",
    "Evaluación",
    "Feedback"
])

# Cargar la página seleccionada
if pagina == "Inicio":
    home.pagina_inicio()
elif pagina == "Búsqueda Multimodal":
    search.pagina_busqueda()
elif pagina == "Evaluación":
    evaluation.pagina_evaluacion()
elif pagina == "Feedback":
    feedback.pagina_feedback()
