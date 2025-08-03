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