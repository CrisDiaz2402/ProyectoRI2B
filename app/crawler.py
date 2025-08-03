#--------------------Para descargar el msrvtt ----------------------------
# import kagglehub
# import shutil
# import os

# def descargar_msr_vtt(destino="data/raw/msrvtt"):
#     print("Descargando MSR-VTT desde Kaggle...")
#     path_descarga = kagglehub.dataset_download("vishnutheepb/msrvtt")
    
#     # Crea la carpeta de destino si no existe
#     os.makedirs(destino, exist_ok=True)
    
#     # Copia los archivos descargados a tu estructura
#     for archivo in os.listdir(path_descarga):
#         origen = os.path.join(path_descarga, archivo)
#         destino_archivo = os.path.join(destino, archivo)
#         shutil.move(origen, destino_archivo)
    
#     print("✅ Dataset MSR-VTT descargado y copiado a:", destino) 

# import os
# import subprocess

# def descargar_youtube8m(shards=15, mirror="us"):
#     base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "youtube8m"))
#     os.makedirs(base_path, exist_ok=True)

#     script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "download.py"))

#     for i in range(1, shards + 1):
#         env = os.environ.copy()
#         env["partition"] = "2/video/train"
#         env["mirror"] = mirror
#         env["shard"] = f"{i},100"

#         print(f"Descargando shard {i}/{shards} en {base_path}...")

#         # Ejecuta el script usando python, pasando variables de entorno
#         subprocess.run(
#             ["python", script_path],
#             env=env,
#             cwd=base_path,
#             check=True
#         )
#     print("✅ Descarga parcial completada.")
        
#-------------------------Para hacer crawling de imágenes con DuckDuckGo Search en tiempo real----------------------------

from ddgs import DDGS
import os
import requests
from tqdm import tqdm

def buscar_y_descargar_imagenes_ddgs(query, max_images=10, carpeta_destino="data/raw/crawled"):
    print(f"Buscando imágenes para: {query}")
    os.makedirs(carpeta_destino, exist_ok=True)

    with DDGS() as ddgs:
        resultados = ddgs.images(query, max_results=max_images)
        for idx, resultado in enumerate(tqdm(resultados, desc="Descargando")):
            url_img = resultado['image']
            ext = url_img.split('.')[-1].split('?')[0]
            filename = os.path.join(carpeta_destino, f"{query}_{idx}.{ext}")

            try:
                img_data = requests.get(url_img, timeout=5).content
                with open(filename, "wb") as f:
                    f.write(img_data)
            except Exception as e:
                print(f"Error con {url_img}: {e}")

    print("✅ Descarga completada.")

if __name__ == "__main__":
    buscar_y_descargar_imagenes_ddgs("gatos corriendo", max_images=5)
