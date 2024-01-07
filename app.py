import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

from windows.settings import show_settings_window
from windows.about import show_about_window

from backend.settings import AppSettings
from backend import faster_whisper

import ffmpeg
import os, threading

root = tk.Tk()
root.title("Audio Transcription App")

app_settings = AppSettings()
app_settings.load_settings("settings.json")

progress = None
transcribe_thread = None
stop_transcribe = False

transcriptions = []

def browse_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv"), ("Audio Files", "*.mp3;*.aac;*.wav;*.m4a")])
    if file_path:
        entry_video.delete(0, tk.END)
        entry_video.insert(tk.END, file_path)
        if model_ready_var.get() == 'true':
            button_transcribe['state'] = 'normal'

def stop():
    global transcribe_thread
    if transcribe_thread:
        global stop_transcribe
        stop_transcribe = True
    button_transcribe.config(text="Transcribe Audio", command=transcribe_audio)

def transcribe_audio():
    global progress
    try:
        audio = entry_video.get()
        if audio.endswith(('mp4', 'mkv', 'avi')):
            probe = ffmpeg.probe(audio)
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']

            if audio_streams:
                ext = audio_streams[0]['codec_name']
            else:
                raise Exception
            if os.path.exists("./tmp." + ext):
                os.remove("./tmp." + ext)
            ffmpeg.input(audio).output("./tmp." + ext, acodec='copy').run()
            audio = "./tmp." + ext
    except Exception as e:
        print(f"Error stripping audio: {e}")
    
    probe = ffmpeg.probe(audio)
    stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    duration = float(stream['duration'])

    if progress:
        progress.grid_forget()

    progress_var, progress = show_progress_bar()

    text_area.delete('1.0', tk.END)
    button_save['state'] = "disabled"
    def _transcribe():
        try:
            segments, info = faster_whisper.transcribe_audio(audio, app_settings)
        except:
            progress_var.set(100)
            text_area.insert(tk.END, f"Failed. Please try cleaning models folder!\n")
            button_transcribe.config(text="Transcribe Audio", command=transcribe_audio)
            return

    
        text_area.insert(tk.END, "Detected language '%s' with probability %f\n\n" % (info.language, info.language_probability))

        for segment in segments:
            global stop_transcribe
            if stop_transcribe:
                return
            global transcriptions
            transcriptions.append((segment.start, segment.end, segment.text.lstrip()))
            button_save['state'] = "normal"
            text_area.insert(tk.END, f"[{faster_whisper.convert_seconds_to_hms(segment.start)} -> {faster_whisper.convert_seconds_to_hms(segment.end)}] {segment.text.lstrip()}\n")
            progress_var.set(int(segment.end/duration*100))
            text_area.yview_pickplace("end")

        text_area.insert(tk.END, "\nFinished transcribing!\n")
        progress_var.set(100)
        button_transcribe.config(text="Transcribe Audio", command=transcribe_audio)
        
    stop()
    global transcribe_thread
    button_transcribe.config(text="Stop", command=stop)
    global stop_transcribe
    stop_transcribe = False
    transcribe_thread = threading.Thread(target=_transcribe, name="transcribe")
    transcribe_thread.daemon = True
    transcribe_thread.start()

def save_transcription():
    from datetime import timedelta
    transcription_content = ""
    count = 0
    for line in transcriptions:
        startTime = str(0)+str(timedelta(seconds=int(line[0])))+',000'
        endTime = str(0)+str(timedelta(seconds=int(line[1])))+',000'
        text = line[2]
        segmentId = count + 1
        transcription_content += f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"

        count += 1

    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Subtitle Files", "*.srt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(transcription_content)

def show_progress_bar():
    progress = tk.Frame(root)
    progress.grid(row=3, column=0, sticky="we")
    progress.columnconfigure(0, weight=1)

    progress_var = tk.IntVar(progress, 0)
    progress_bar = ttk.Progressbar(progress, orient="horizontal", mode="determinate", variable=progress_var)
    progress_bar.grid(row=0, column=0, pady=10, padx=(110,85), sticky="we")
    return progress_var, progress

def watch_model_state():
    button_transcribe['state'] = 'normal' if model_ready_var.get() == 'true' and entry_video.get() else 'disabled'

def on_model_change(job):
    global t
    if not job:
        t = faster_whisper.check(app_settings.model_var.get(), text_area, model_ready_var)
    elif job.name != app_settings.model_var.get():
        t = faster_whisper.check(app_settings.model_var.get(), text_area, model_ready_var)

# menus
menu_bar = tk.Menu(root)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=browse_video)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)
menu_bar.add_cascade(label="File", menu=file_menu)

settings_menu = tk.Menu(menu_bar, tearoff=0)
settings_menu.add_command(label="Settings", command=lambda: show_settings_window(root, app_settings))
menu_bar.add_cascade(label="Settings", menu=settings_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=lambda: show_about_window(root))
menu_bar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menu_bar)

# video load area
video_load = tk.Frame(root)
video_load.grid(row=0, column=0, sticky="we")
video_load.columnconfigure(1, weight=1)

label_video = tk.Label(video_load, text="Video File:")
label_video.grid(row=0, column=0, padx=10, pady=10)

entry_video = tk.Entry(video_load)
entry_video.grid(row=0, column=1, padx=(28,10), pady=10, sticky="ew")

button_browse = tk.Button(video_load, text="Browse", command=browse_video)
button_browse.grid(row=0, column=2, padx=10, pady=10)

# transcription area
transcription = tk.Frame(root)
transcription.grid(row=1, column=0, sticky="nswe")
transcription.columnconfigure(1, weight=1)
transcription.rowconfigure(0, weight=1)

label_text = tk.Label(transcription, text="Transcription:")
label_text.grid(row=0, column=0, sticky="w", padx=10, pady=10)

text_area = scrolledtext.ScrolledText(transcription, wrap=tk.WORD)
text_area.grid(row=0, column=1, padx=(8,69), pady=10, sticky="nsew")

# buttons area
buttons = tk.Frame(root)
buttons.grid(row=2, column=0, sticky="we")
buttons.columnconfigure(0, weight=1)
buttons.columnconfigure(1, weight=1)

button_transcribe = tk.Button(buttons, text="Transcribe Audio", command=transcribe_audio, state="disabled")
button_transcribe.grid(row=0, column=0, pady=10)

button_save = tk.Button(buttons, text="Save as Subtitles", command=save_transcription, state="disabled")
button_save.grid(row=0, column=1, pady=10)

root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

model_ready_var = tk.StringVar(root, 'false')
model_ready_var.trace_add("write", lambda *args: watch_model_state())
app_settings.model_var.trace_add("write", lambda *args: on_model_change(t))
t = faster_whisper.check(app_settings.model_var.get(), text_area, model_ready_var)
root.mainloop()
