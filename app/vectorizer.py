import os
import json
import torch
import clip
from PIL import Image
import numpy as np
from pathlib import Path

# Carga del modelo CLIP y preprocesamiento
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

METADATA_PATH = "data/metadata.json"

def save_metadata_entry(vector_name, original_path, metadata_path=METADATA_PATH):
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    metadata[vector_name] = original_path.replace("\\", "/")  # Normaliza separadores para compatibilidad
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

def vectorize_image(image_path):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
    image_features /= image_features.norm(dim=-1, keepdim=True)
    return image_features.cpu().numpy()[0]

def vectorize_text(text):
    max_length = 77
    text_input = clip.tokenize([text], truncate=True).to(device)
    if text_input.shape[1] > max_length:
        text_input = text_input[:, :max_length]
    with torch.no_grad():
        text_features = model.encode_text(text_input)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    return text_features.cpu().numpy()[0]

def vectorize_and_save_images(image_dir, output_dir, max_files=None):
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []

    for root, _, files in os.walk(image_dir):
        for file in sorted(files):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_paths.append(os.path.join(root, file))

    for image_path in image_paths:
        vector = vectorize_image(image_path)

        rel_path = os.path.relpath(image_path, image_dir)
        base_name = os.path.splitext(rel_path.replace(os.sep, "_"))[0]
        output_path = os.path.join(output_dir, f"{base_name}_vec.npy")
        np.save(output_path, vector)

        # ✅ Buscar si este frame proviene de un video (por nombre de carpeta)
        original_path = None
        path_parts = Path(image_path).parts
        if "frames" in path_parts:
            try:
                idx = path_parts.index("frames")
                video_folder = path_parts[idx + 1]  # nombre del video sin extensión
                video_dirs = ["data/dbtest/videos"]  # otros posibles folders de videos

                for base_dir in video_dirs:
                    for ext in [".mp4", ".webm", ".mkv"]:
                        candidate = os.path.join(base_dir, video_folder + ext)
                        if os.path.exists(candidate):
                            original_path = candidate
                            break
                    if original_path:
                        break
            except Exception:
                pass

        # Si no es un frame o no se encontró video original, guarda la imagen directamente
        if original_path:
            save_metadata_entry(base_name, original_path)
        else:
            save_metadata_entry(base_name, image_path)

        print(f"[✔] Vector guardado para imagen {image_path}")

def vectorize_and_save_texts(text_dir, output_dir, max_files=None):
    os.makedirs(output_dir, exist_ok=True)
    files = [f for f in os.listdir(text_dir) if f.endswith(".txt")]
    files = sorted(files)

    for file in files:
        text_path = os.path.join(text_dir, file)
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        # 🔴 FILTRO DE TEXTOS BASURA
        if not text or len(text) < 10 or "undefined" in text.lower():
            print(f"[⛔] Ignorado archivo: {file} por ser basura.")
            continue

        vector = vectorize_text(text)
        base_name = os.path.splitext(file)[0]
        output_path = os.path.join(output_dir, f"{base_name}_vec.npy")
        np.save(output_path, vector)

        # ✅ Buscar archivo original (audio o video) a partir del nombre base
        original_media_extensions = [".mp4", ".webm", ".mkv", ".mp3", ".wav"]
        media_base_dirs = [
            "data/dbtest/videos",                      # videos
            "data/dbtest/audios"                       # audios 
        ]
        original_path = None
        for base_dir in media_base_dirs:
            for ext in original_media_extensions:
                candidate = os.path.join(base_dir, base_name + ext)
                if os.path.exists(candidate):
                    original_path = candidate
                    break
            if original_path:
                break

        # ✅ Guardar en metadata.json la ruta real si se encontró
        if original_path:
            save_metadata_entry(base_name, original_path)
        else:
            # Fallback: guarda el .txt si no encuentra original
            save_metadata_entry(base_name, text_path)

        print(f"[✔] Vector guardado para texto {file}")