#
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity

def cargar_vectores(embedding_dir):
    """
    Carga todos los vectores en una carpeta y devuelve una lista de tuplas (nombre_archivo, vector).
    """
    vectores = []
    for root, _, files in os.walk(embedding_dir):
        for file in files:
            if file.endswith("_vec.npy"):
                path = os.path.join(root, file)
                vector = np.load(path)
                vectores.append((file.replace("_vec.npy", ""), vector))
    return vectores

def buscar_similares(vector_consulta, embedding_dir, top_k=5):
    """
    Busca los top_k vectores más similares al vector de consulta.
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
