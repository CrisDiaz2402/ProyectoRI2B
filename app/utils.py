from PIL import Image
def calcular_histograma_imagen(imagen, bins=256):
    """
    Calcula un histograma normalizado de una imagen PIL.Image, ruta de imagen o archivo subido (Streamlit UploadedFile).
    Devuelve un vector 1D concatenando los histogramas de cada canal.
    """
    import io
    import numpy as np
    # Si es UploadedFile de Streamlit
    if hasattr(imagen, 'read') and not isinstance(imagen, str):
        # Resetear el puntero al inicio para asegurarse de que se puede leer
        imagen.seek(0)
        # Lee el buffer una sola vez y lo reutiliza
        contenido = imagen.read()
        buffer = io.BytesIO(contenido)
        imagen_pil = Image.open(buffer)
        imagen_pil.load()  # fuerza la carga
        imagen = imagen_pil
    elif isinstance(imagen, str):
        imagen = Image.open(imagen)
    # Si es PIL.Image
    if imagen.mode != 'RGB':
        imagen = imagen.convert('RGB')
    arr = np.array(imagen)
    hist = []
    for i in range(3):  # R, G, B
        h, _ = np.histogram(arr[..., i], bins=bins, range=(0, 256), density=True)
        hist.append(h)
    hist = np.concatenate(hist)
    return hist.astype(np.float32)
import numpy as np
import os
import json
from sklearn.metrics.pairwise import cosine_similarity

METADATA_REAL_PATH = "data/processed/metadata-real.json"

def cargar_vectores(embedding_dir):
    """
    Carga todos los vectores desde los archivos *_vec.npy dentro del directorio dado.
    """
    vectores = []
    for root, _, files in os.walk(embedding_dir):
        for file in files:
            if file.endswith("_vec.npy"):
                path = os.path.join(root, file)
                vector = np.load(path)
                nombre = file.replace("_vec.npy", "")
                vectores.append((nombre, vector))
    return vectores

def buscar_similares(vector_consulta, embedding_dir, top_k=10, histograma_consulta=None):
    """
    Retorna los top_k vectores más similares al vector de consulta usando similitud coseno y, para imágenes, también similitud de histogramas.
    Si se proporciona histograma_consulta, se compara con los histogramas de la base para imágenes.
    """
    vectores = cargar_vectores(embedding_dir)
    if not vectores:
        return []

    nombres, vecs = zip(*vectores)
    vecs = np.array(vecs)

    similitudes = cosine_similarity([vector_consulta], vecs)[0]
    # Pre-filtrado: solo nombres con metadata válida
    nombres_validos = []
    similitudes_validas = []
    rutas_validas = []
    for i, nombre in enumerate(nombres):
        meta = get_original_path(nombre)
        if meta is not None and meta.get("path"):
            nombres_validos.append(nombre)
            similitudes_validas.append(similitudes[i])
            rutas_validas.append(meta.get("path"))
    if not nombres_validos:
        return []

    # --- Similitud de histogramas para imágenes ---
    def cargar_histograma(nombre):
        # Busca histograma por nombre base en data/processed/histograms
        hist_path = os.path.join("data/processed/histograms", nombre + ".npy")
        if os.path.exists(hist_path):
            return np.load(hist_path)
        return None

    def calcular_similitud_histogramas(hist1, hist2):
        # Usa correlación normalizada (puedes cambiar a otra métrica si prefieres)
        if hist1 is None or hist2 is None:
            return 0.0
        # Normaliza
        hist1 = hist1.astype(np.float32)
        hist2 = hist2.astype(np.float32)
        if np.linalg.norm(hist1) == 0 or np.linalg.norm(hist2) == 0:
            return 0.0
        return float(np.dot(hist1, hist2) / (np.linalg.norm(hist1) * np.linalg.norm(hist2)))

    # Penalización por metadata incompleta
    penalizaciones = []
    scores_hist = []
    for idx, nombre in enumerate(nombres_validos):
        meta = get_original_path(nombre)
        penalizacion = 0.0
        if not meta.get("metadata") or len(meta.get("metadata", {})) < 1:
            penalizacion += 0.10  # penaliza si no hay metadata
        penalizaciones.append(penalizacion)

        # Si es imagen, calcula similitud de histogramas
        ruta = rutas_validas[idx].lower()
        if ruta.endswith(('.jpg', '.jpeg', '.png')):
            hist_base = cargar_histograma(nombre)
            if histograma_consulta is not None:
                score_hist = calcular_similitud_histogramas(histograma_consulta, hist_base)
            else:
                score_hist = 0.0
            scores_hist.append(score_hist)
        else:
            scores_hist.append(0.0)

    # Combina score de vectores y de histogramas (para imágenes)
    alpha = 0.8  # peso para similitud de vectores
    beta = 0.2   # peso para similitud de histogramas
    scores_ajustados = []
    for i, nombre in enumerate(nombres_validos):
        ruta = rutas_validas[i].lower()
        if ruta.endswith(('.jpg', '.jpeg', '.png')):
            score = alpha * similitudes_validas[i] + beta * scores_hist[i] - penalizaciones[i]
        else:
            score = similitudes_validas[i] - penalizaciones[i]
        scores_ajustados.append(score)

    # Ranking por score ajustado
    indices = np.argsort(scores_ajustados)[::-1][:top_k]
    resultados = [(nombres_validos[i], scores_ajustados[i]) for i in indices]
    return resultados
    # --- Feedback: cargar y calcular bonus/penalización ---
    def cargar_feedback():
        feedback_path = "data/processed/feedback.json"
        if os.path.exists(feedback_path):
            with open(feedback_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    feedback = cargar_feedback()

    penalizaciones = []
    bonuses = []
    feedback_keys_usadas = []  # Para depuración
    for nombre in nombres_validos:
        meta = get_original_path(nombre)
        penalizacion = 0.0
        if not meta.get("metadata") or len(meta.get("metadata", {})) < 1:
            penalizacion += 0.10  # penaliza si no hay metadata
        penalizaciones.append(penalizacion)

        # --- Buscar feedback: exacto o parcial ---
        fb = feedback.get(nombre)
        feedback_key = nombre
        if fb is None:
            # Buscar por coincidencia parcial (nombre base)
            nombre_base = nombre.lower()
            for k in feedback.keys():
                if k.lower() in nombre_base or nombre_base in k.lower():
                    fb = feedback[k]
                    feedback_key = k
                    break
        if fb is None:
            fb = {}
        feedback_keys_usadas.append(feedback_key)

        # Bonus feedback
        bonus = 0.0
        bonus += 0.05 * fb.get("likes", 0)
        bonus -= 0.05 * fb.get("dislikes", 0)
        bonus += 0.01 * fb.get("clics", 0)
        if fb.get("estrellas"):
            try:
                promedio = sum(fb["estrellas"]) / len(fb["estrellas"])
                bonus += 0.02 * (promedio - 3)  # centrado en 3 estrellas
            except Exception:
                pass
        bonuses.append((bonus, feedback_key))

    # Score ajustado: similitud - penalización + bonus_feedback
    scores_ajustados = [s - p + b[0] for s, p, b in zip(similitudes_validas, penalizaciones, bonuses)]
    # Ranking por score ajustado
    indices = np.argsort(scores_ajustados)[::-1][:top_k]
    resultados = [(nombres_validos[i], scores_ajustados[i], bonuses[i][0], bonuses[i][1]) for i in indices]
    # Mostrar comparativa en consola
    print("\n[Comparación nombre vector vs clave feedback usada]:")
    for i in indices:
        print(f"  Vector: {nombres_validos[i]}  |  Feedback key usada: {bonuses[i][1]}")
    return resultados

def get_original_path(nombre_vector):
    """
    Busca la ruta original y metadatos del archivo asociado al vector usando metadata-real.json.
    Coincide por nombre base (sin extensión) en todas las secciones.
    Devuelve un dict con filename, path y metadata si encuentra, o None si no.
    """
    if not os.path.exists(METADATA_REAL_PATH):
        return None
    with open(METADATA_REAL_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    nombre_base = nombre_vector.lower()
    for seccion in metadata.values():
        if not isinstance(seccion, list):
            continue
        for item in seccion:
            filename = item.get("filename", "").lower()
            # Coincidencia exacta sin extensión
            if filename:
                base = os.path.splitext(filename)[0]
                if base == nombre_base:
                    return item
    return None

def clasificar_resultados_por_tipo(resultados):
    """
    Agrupa resultados en categorías: textos, imágenes, videos, audios, otros, usando metadata-real.json.
    Devuelve también los metadatos completos para cada resultado.
    """
    categorias = {"textos": [], "imagenes": [], "videos": [], "audios": [], "otros": []}
    print("\n[Depuración] Resultados recibidos:")
    for tupla in resultados:
        # Soporta (nombre, score, bonus, feedback_key) o (nombre, score)
        if len(tupla) == 4:
            nombre, score, bonus, feedback_key = tupla
        elif len(tupla) == 3:
            nombre, score, bonus = tupla
            feedback_key = nombre
        else:
            nombre, score = tupla
            bonus = 0.0
            feedback_key = nombre
        meta = get_original_path(nombre)
        if meta:
            ruta = meta.get("path", "").lower()
        else:
            ruta = None
        print(f"  - Nombre vector: {nombre} | Score: {score:.3f} | Bonus: {bonus:.3f} | FeedbackKey: {feedback_key} | Ruta: {ruta}")
        if not ruta:
            print(f"  [ADVERTENCIA] No se encontró ruta en metadata-real.json para: {nombre}")
            continue
        # Enriquecer info: resumen de metadata
        detalles = ""
        if meta:
            detalles_items = []
            if meta.get("metadata"):
                for k, v in meta["metadata"].items():
                    detalles_items.append(f"{k}: {v}")
            if detalles_items:
                detalles = " | ".join(detalles_items)
        enriched_meta = meta.copy() if meta else {}
        enriched_meta["detalles"] = detalles
        enriched_meta["bonus_feedback"] = bonus
        enriched_meta["feedback_key"] = feedback_key
        if ruta.endswith(".txt"):
            categorias["textos"].append((nombre, score, enriched_meta))
        elif ruta.endswith((".jpg", ".jpeg", ".png")):
            categorias["imagenes"].append((nombre, score, enriched_meta))
        elif ruta.endswith((".mp4", ".webm")):
            categorias["videos"].append((nombre, score, enriched_meta))
        elif ruta.endswith((".mp3", ".wav")):
            categorias["audios"].append((nombre, score, enriched_meta))
        else:
            categorias["otros"].append((nombre, score, enriched_meta))
    print("[Depuración] Conteo por categoría:")
    for cat, items in categorias.items():
        print(f"  - {cat}: {len(items)} resultados")
    return categorias
    for tupla in resultados:
        # Soporta (nombre, score, bonus) o (nombre, score)
        if len(tupla) == 3:
            nombre, score, bonus = tupla
        else:
            nombre, score = tupla
            bonus = 0.0
        meta = get_original_path(nombre)
        if meta:
            ruta = meta.get("path", "").lower()
        else:
            ruta = None
        print(f"  - Nombre vector: {nombre} | Score: {score:.3f} | Bonus: {bonus:.3f} | Ruta: {ruta}")
        if not ruta:
            print(f"  [ADVERTENCIA] No se encontró ruta en metadata-real.json para: {nombre}")
            continue
        # Enriquecer info: resumen de metadata
        detalles = ""
        if meta:
            detalles_items = []
            if meta.get("metadata"):
                for k, v in meta["metadata"].items():
                    detalles_items.append(f"{k}: {v}")
            if detalles_items:
                detalles = " | ".join(detalles_items)
        enriched_meta = meta.copy() if meta else {}
        enriched_meta["detalles"] = detalles
        enriched_meta["bonus_feedback"] = bonus
        if ruta.endswith(".txt"):
            categorias["textos"].append((nombre, score, enriched_meta))
        elif ruta.endswith((".jpg", ".jpeg", ".png")):
            categorias["imagenes"].append((nombre, score, enriched_meta))
        elif ruta.endswith((".mp4", ".webm")):
            categorias["videos"].append((nombre, score, enriched_meta))
        elif ruta.endswith((".mp3", ".wav")):
            categorias["audios"].append((nombre, score, enriched_meta))
        else:
            categorias["otros"].append((nombre, score, enriched_meta))
    print("[Depuración] Conteo por categoría:")
    for cat, items in categorias.items():
        print(f"  - {cat}: {len(items)} resultados")
    return categorias