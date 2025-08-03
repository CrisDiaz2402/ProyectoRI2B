import os
from app.processor import process_video_file, process_image_file, transcribe_audio

VIDEO_DIRS = [
    "data/raw/msrvtt",
]

IMAGE_DIRS = [
    "data/raw/crawled",
    "data/raw/flickr"
]

AUDIO_DIRS = [
    "data/raw/audios/ingles/clips",
    # "data/raw/audios/espanol/clips"
]

FRAMES_OUTPUT = "data/processed/frames"
TRANSCRIPTS_OUTPUT = "data/processed/transcripts"
HISTOGRAMS_OUTPUT = "data/processed/histograms"

MAX_FILES = 10

def process_all_videos():
    for directory in VIDEO_DIRS:
        if not os.path.exists(directory):
            continue

        files = [f for f in os.listdir(directory) if f.endswith((".mp4", ".webm", ".mkv"))]
        files = sorted(files)[:MAX_FILES]

        for file in files:
            video_path = os.path.join(directory, file)
            print(f"📹 Procesando video: {video_path}")
            process_video_file(video_path, FRAMES_OUTPUT, TRANSCRIPTS_OUTPUT)

def process_all_images():
    for directory in IMAGE_DIRS:
        if not os.path.exists(directory):
            continue

        files = [f for f in os.listdir(directory) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
        files = sorted(files)[:MAX_FILES]

        for file in files:
            image_path = os.path.join(directory, file)
            print(f"🖼️ Procesando imagen: {image_path}")
            process_image_file(image_path, HISTOGRAMS_OUTPUT)

def process_all_audios():
    for directory in AUDIO_DIRS:
        if not os.path.exists(directory):
            continue

        files = [f for f in os.listdir(directory) if f.endswith((".mp3", ".wav"))]
        files = sorted(files)[:MAX_FILES]

        for file in files:
            audio_path = os.path.join(directory, file)
            print(f"🎧 Transcribiendo audio: {audio_path}")
            text = transcribe_audio(audio_path)
            audio_name = os.path.splitext(file)[0]
            output_path = os.path.join(TRANSCRIPTS_OUTPUT, f"{audio_name}.txt")

            os.makedirs(TRANSCRIPTS_OUTPUT, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

if __name__ == "__main__":
    print("🚀 Iniciando procesamiento multimedia en lote...")
    process_all_videos()
    process_all_images()
    process_all_audios()
    print("✅ Procesamiento completado.")