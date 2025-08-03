import os
import torch
import clip
from PIL import Image
import numpy as np

# Carga del modelo CLIP y preprocesamiento
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def vectorize_image(image_path):
    """
    Vectoriza una imagen con CLIP.
    """
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
    image_features /= image_features.norm(dim=-1, keepdim=True)
    return image_features.cpu().numpy()[0]

def vectorize_text(text):
    """
    Vectoriza texto con CLIP.
    Trunca el texto si es demasiado largo para el tokenizador (máximo 77 tokens).
    """
    max_length = 77  # Máximo tokens que CLIP soporta

    # Tokenizar el texto completo con truncamiento automático
    text_input = clip.tokenize([text], truncate=True).to(device)

    # En caso que el tokenizador no trunque bien (ejemplo: versiones antiguas),
    # hacemos una verificación y recortamos si es necesario:
    if text_input.shape[1] > max_length:
        text_input = text_input[:, :max_length]

    with torch.no_grad():
        text_features = model.encode_text(text_input)

    text_features /= text_features.norm(dim=-1, keepdim=True)
    return text_features.cpu().numpy()[0]

def vectorize_and_save_images(image_dir, output_dir, max_files=None):
    """
    Vectoriza imágenes (incluyendo subdirectorios) y guarda vectores en output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []

    for root, _, files in os.walk(image_dir):
        for file in sorted(files):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_paths.append(os.path.join(root, file))
            if max_files is not None and len(image_paths) >= max_files:
                break
        if max_files is not None and len(image_paths) >= max_files:
            break

    for image_path in image_paths:
        vector = vectorize_image(image_path)
        # Nombre de archivo basado en ruta relativa para evitar conflictos
        rel_path = os.path.relpath(image_path, image_dir)
        base_name = os.path.splitext(rel_path.replace(os.sep, "_"))[0]
        output_path = os.path.join(output_dir, f"{base_name}_vec.npy")
        np.save(output_path, vector)
        print(f"[✔] Vector guardado para imagen {image_path}")

def vectorize_and_save_texts(text_dir, output_dir, max_files=None):
    """
    Vectoriza archivos .txt en text_dir (hasta max_files si se especifica)
    y guarda vectores en output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    files = [f for f in os.listdir(text_dir) if f.endswith(".txt")]
    files = sorted(files)
    if max_files is not None:
        files = files[:max_files]

    for file in files:
        text_path = os.path.join(text_dir, file)
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
        vector = vectorize_text(text)
        output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_vec.npy")
        np.save(output_path, vector)
        print(f"[✔] Vector guardado para texto {file}")