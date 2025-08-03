import os
import cv2
import numpy as np
import whisper
from moviepy.video.io.VideoFileClip import VideoFileClip

# ============================
# 📌 FRAMES: Extracción de video clips
# ============================

def extract_frames(video_path, output_dir, frame_interval=30):
    os.makedirs(output_dir, exist_ok=True)
    video = cv2.VideoCapture(video_path)

    count = 0
    frame_id = 0
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        if count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{frame_id:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_id += 1
        count += 1

    video.release()
    print(f"[✔] Frames extraídos de {video_path} → {output_dir}")

# ============================
# 📌 AUDIO: Verificar presencia y transcripción
# ============================

def has_audio_stream(video_path):
    try:
        clip = VideoFileClip(video_path)
        has_audio = clip.audio is not None
        clip.close()
        return has_audio
    except Exception:
        return False

def transcribe_audio(audio_path, model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    print(f"[✔] Transcripción completada para {audio_path}")
    return result["text"]

# ============================
# 📌 IMAGEN: Histograma
# ============================

def compute_histogram(image_path):
    image = cv2.imread(image_path)
    chans = cv2.split(image)
    features = []
    for chan in chans:
        hist = cv2.calcHist([chan], [0], None, [256], [0, 256])
        features.append(hist.flatten())
    full_hist = np.concatenate(features)
    print(f"[✔] Histograma calculado para {image_path}")
    return full_hist

# ============================
# 📌 PROCESAMIENTO DE ARCHIVOS
# ============================

def process_video_file(video_path, frames_dir, transcripts_dir):
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Extraer frames
    frame_output_path = os.path.join(frames_dir, video_name)
    extract_frames(video_path, frame_output_path)

    # Transcribir si tiene audio
    if has_audio_stream(video_path):
        transcript = transcribe_audio(video_path)
        os.makedirs(transcripts_dir, exist_ok=True)
        transcript_output_path = os.path.join(transcripts_dir, f"{video_name}.txt")
        with open(transcript_output_path, "w", encoding="utf-8") as f:
            f.write(transcript)
    else:
        print(f"[⚠️] El video {video_path} no contiene pista de audio. Se omitió la transcripción.")

def process_image_file(image_path, histogram_dir):
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    histogram = compute_histogram(image_path)
    os.makedirs(histogram_dir, exist_ok=True)
    histogram_path = os.path.join(histogram_dir, f"{image_name}.npy")
    np.save(histogram_path, histogram)