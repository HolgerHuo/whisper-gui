import tkinter as tk
from tkinter import ttk
import webbrowser

def open_project_link():
    project_url = "https://github.com/HolgerHuo/whisper-gui"
    webbrowser.open(project_url)

def show_about_window(root):
    about_window = tk.Toplevel(root)
    about_window.title("About")

    about_window.columnconfigure(0, weight=1)
    about_window.rowconfigure(3, weight=1)

    label_author = ttk.Label(about_window, text="Author: Holger Huo")
    label_author.grid(row=0, column=0, padx=10, pady=(10, 0))

    label_project = ttk.Label(about_window, text="Project: Whisper GUI")
    label_project.grid(row=1, column=0, padx=10, pady=(10, 0))

    label_license = ttk.Label(about_window, text="License: GPL-v3")
    label_license.grid(row=2, column=0, padx=10, pady=10)

    link_project = ttk.Label(about_window, text="Visit Project", cursor="hand2", foreground="blue")
    link_project.grid(row=3, column=0, padx=10, pady=(10, 0))
    link_project.bind("<Button-1>", lambda e: open_project_link())
