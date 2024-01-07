import threading

import tkinter as tk

from faster_whisper import WhisperModel
from faster_whisper.utils import download_model

# init variables
TMP_DIR="./tmp"
MODELS_DIR="./models/"

def check(model_size, text_area, model_ready_var):
    try:
        download_model(size_or_id=model_size, cache_dir=MODELS_DIR, local_files_only=True)
        text_area.insert(tk.END, f"Loaded model: {model_size}\n")
        model_ready_var.set('true')
        return
    except:
        model_ready_var.set('false')
        t = threading.Thread(target=lambda: download(model_size, text_area, model_ready_var), name=model_size)
        t.daemon = True
        t.start()
        return t

def download(model_size, text_area, model_ready_var):
    try:
        text_area.insert(tk.END, f"Downloading model: {model_size}\n")
        download_model(size_or_id=model_size, cache_dir=MODELS_DIR)
        text_area.insert(tk.END, f"Loaded model: {model_size}\n")
        model_ready_var.set('true')
    except Exception as e:
        print(f"Cannot download '{model_size}' model: {e}")
        download(model_size, text_area, model_ready_var)

def convert_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return output

def transcribe_audio(audio_file, app_settings):
    model = WhisperModel(app_settings.model_var.get(), device=app_settings.device_var.get(), compute_type=app_settings.compute_type_var.get(), cpu_threads=int(app_settings.cpu_threads_var.get()), local_files_only=True, download_root=MODELS_DIR)

    try:
        return model.transcribe(audio_file, beam_size=5)
    except Exception as e:
        return False
