import numpy as np
import os
import json
from sklearn.metrics.pairwise import cosine_similarity

METADATA_PATH = "data/metadata.json"

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
    indices = np.argsort(similitudes)[::-1][:top_k]

    resultados = [(nombres[i], similitudes[i]) for i in indices]
    return resultados

def get_original_path(nombre_vector):
    """
    Devuelve la ruta original del archivo asociado al vector usando metadata.json.
    """
    if not os.path.exists(METADATA_PATH):
        return None
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return metadata.get(nombre_vector)

def clasificar_resultados_por_tipo(resultados):
    """
    Agrupa resultados en categorías: textos, imágenes, videos, audios, otros.
    """
    categorias = {"textos": [], "imagenes": [], "videos": [], "audios": [], "otros": []}
    print("\n[Depuración] Resultados recibidos:")
    for nombre, score in resultados:
        ruta = get_original_path(nombre)
        print(f"  - Nombre vector: {nombre} | Score: {score:.3f} | Ruta: {ruta}")
        if not ruta:
            print(f"  [ADVERTENCIA] No se encontró ruta en metadata.json para: {nombre}")
            continue
        ruta = ruta.lower()
        if ruta.endswith(".txt"):
            categorias["textos"].append((nombre, score))
        elif ruta.endswith((".jpg", ".jpeg", ".png")):
            categorias["imagenes"].append((nombre, score))
        elif ruta.endswith((".mp4", ".webm")):
            categorias["videos"].append((nombre, score))
        elif ruta.endswith((".mp3", ".wav")):
            categorias["audios"].append((nombre, score))
        else:
            categorias["otros"].append((nombre, score))
    print("[Depuración] Conteo por categoría:")
    for cat, items in categorias.items():
        print(f"  - {cat}: {len(items)} resultados")
    return categorias