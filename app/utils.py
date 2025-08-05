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

def buscar_similares(vector_consulta, embedding_dir, top_k=10):
    """
    Retorna los top_k vectores más similares al vector de consulta usando similitud coseno.
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
    for i, nombre in enumerate(nombres):
        meta = get_original_path(nombre)
        if meta is not None and meta.get("path"):
            nombres_validos.append(nombre)
            similitudes_validas.append(similitudes[i])
    if not nombres_validos:
        return []

    # Penalización por metadata incompleta
    penalizaciones = []
    for nombre in nombres_validos:
        meta = get_original_path(nombre)
        penalizacion = 0.0
        if not meta.get("metadata") or len(meta.get("metadata", {})) < 1:
            penalizacion += 0.10  # penaliza si no hay metadata
        # Puedes agregar más penalizaciones aquí (ej: idioma, duración, etc)
        penalizaciones.append(penalizacion)

    # Ajuste de score
    scores_ajustados = [s - p for s, p in zip(similitudes_validas, penalizaciones)]
    # Ranking por score ajustado
    indices = np.argsort(scores_ajustados)[::-1][:top_k]
    resultados = [(nombres_validos[i], scores_ajustados[i]) for i in indices]
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
    for nombre, score in resultados:
        meta = get_original_path(nombre)
        if meta:
            ruta = meta.get("path", "").lower()
        else:
            ruta = None
        print(f"  - Nombre vector: {nombre} | Score: {score:.3f} | Ruta: {ruta}")
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