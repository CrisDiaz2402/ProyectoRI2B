import os
import json
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen import File as AudioFile
import ffmpeg

# Carpeta base
RAW_DIR = 'data/dbtest'
OUTPUT_PATH = 'data/processed/metadata-real.json'

# Tipos de archivo
IMAGE_EXTS = ['.jpg', '.jpeg', '.png']
AUDIO_EXTS = ['.mp3', '.wav']
VIDEO_EXTS = ['.mp4', '.mov', '.mkv']
TEXT_EXTS = ['.txt', '.md']

# Función para extraer metadata de imagen
def extract_image_metadata(file_path):
    metadata = {}
    try:
        img = Image.open(file_path)
        exif_data = img._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[str(tag)] = str(value)
    except Exception as e:
        metadata['error'] = str(e)
    return metadata

# Función para extraer metadata de audio
def extract_audio_metadata(file_path):
    metadata = {}
    try:
        audio = AudioFile(file_path)
        for key in audio.keys():
            metadata[key] = str(audio[key])
    except Exception as e:
        metadata['error'] = str(e)
    return metadata

# Función para extraer metadata de video
def extract_video_metadata(file_path):
    metadata = {}
    try:
        probe = ffmpeg.probe(file_path)
        metadata = probe.get('format', {})
    except Exception as e:
        metadata['error'] = str(e)
    return metadata

# Función para extraer metadata de texto
def extract_text_metadata(file_path):
    metadata = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            metadata['length'] = len(content)
            metadata['lines'] = content.count('\n') + 1
    except Exception as e:
        metadata['error'] = str(e)
    return metadata

# Función principal
def process_files():
    results = {}
    for folder in os.listdir(RAW_DIR):
        folder_path = os.path.join(RAW_DIR, folder)
        if not os.path.isdir(folder_path) or folder in ['youtube8m']:
            continue

        results[folder] = []
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        for file in files:
            path = os.path.join(folder_path, file)
            ext = os.path.splitext(file)[1].lower()

            if ext in IMAGE_EXTS:
                meta = extract_image_metadata(path)
            elif ext in AUDIO_EXTS:
                meta = extract_audio_metadata(path)
            elif ext in VIDEO_EXTS:
                meta = extract_video_metadata(path)
            elif ext in TEXT_EXTS:
                meta = extract_text_metadata(path)
            else:
                meta = {'unsupported': True}

            results[folder].append({
                'filename': file,
                'path': path,
                'metadata': meta
            })

    # Crear carpeta processed si no existe
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Guardar metadata como JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"✅ Metadata guardada en: {OUTPUT_PATH}")

# Ejecutar solo si se ejecuta directamente (no como módulo)
if __name__ == '__main__':
    process_files()