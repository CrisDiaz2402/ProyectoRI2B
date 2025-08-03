import os
from app.vectorizer import vectorize_and_save_images, vectorize_and_save_texts

FRAMES_OUTPUT = "data/processed/frames"
TRANSCRIPTS_OUTPUT = "data/processed/transcripts"
EMBEDDINGS_OUTPUT = "data/processed/embeddings"

def vectorize_all():
    # Vectorizar todos los frames extraídos de videos
    vectorize_and_save_images(FRAMES_OUTPUT, os.path.join(EMBEDDINGS_OUTPUT, "frames"))

    # Vectorizar solo las primeras 10 imágenes de las carpetas raw
    vectorize_and_save_images("data/raw/crawled", os.path.join(EMBEDDINGS_OUTPUT, "images_crawled"), max_files=10)
    vectorize_and_save_images("data/raw/flickr", os.path.join(EMBEDDINGS_OUTPUT, "images_flickr"), max_files=10)

    # Vectorizar solo los primeros 10 textos en data/raw/texto
    vectorize_and_save_texts("data/raw/texto", os.path.join(EMBEDDINGS_OUTPUT, "texts_raw"), max_files=10)

    # Vectorizar todos los textos transcritos del procesamiento multimedia
    vectorize_and_save_texts(TRANSCRIPTS_OUTPUT, os.path.join(EMBEDDINGS_OUTPUT, "texts_transcripts"))

if __name__ == "__main__":
    print("🚀 Iniciando vectorización de datos...")
    vectorize_all()
    print("✅ Vectorización completada.")