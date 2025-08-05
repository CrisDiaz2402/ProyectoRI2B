import os
from app.vectorizer import vectorize_and_save_images, vectorize_and_save_texts

FRAMES_OUTPUT = "data/processed/frames"
TRANSCRIPTS_OUTPUT = "data/processed/transcripts"
EMBEDDINGS_OUTPUT = "data/processed/embeddings"

def vectorize_all():
    # Vectorizar todos los frames extraídos de videos
    vectorize_and_save_images(FRAMES_OUTPUT, os.path.join(EMBEDDINGS_OUTPUT, "frames"))

    # Vectorizar todas las imágenes de la carpeta dbtest/imagenes
    vectorize_and_save_images("data/dbtest/imagenes", os.path.join(EMBEDDINGS_OUTPUT, "images_crawled"))
    # Vectorizar todos los textos en dbtest/textos
    vectorize_and_save_texts("data/dbtest/textos", os.path.join(EMBEDDINGS_OUTPUT, "texts_raw"))

    # Vectorizar todos los textos transcritos del procesamiento multimedia
    vectorize_and_save_texts(TRANSCRIPTS_OUTPUT, os.path.join(EMBEDDINGS_OUTPUT, "texts_transcripts"))

if __name__ == "__main__":
    print("🚀 Iniciando vectorización de datos...")
    vectorize_all()
    print("✅ Vectorización completada.")