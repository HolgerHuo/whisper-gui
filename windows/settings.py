import tkinter as tk
from tkinter import ttk

def show_settings_window(root, app_settings):
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    label_model = tk.Label(settings_window, text="Model:")
    label_model.grid(row=0, column=0, padx=10, pady=5, sticky="e")

    models = [
        "tiny.en",
        "tiny",
        "base.en",
        "base",
        "small.en",
        "small",
        "medium.en",
        "medium",
        "large-v1",
        "large-v2",
        "large-v3",
        "large"
    ]
    model_dropdown = ttk.Combobox(settings_window, values=models, textvariable=app_settings.model_var)
    model_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    label_device = tk.Label(settings_window, text="Device:")
    label_device.grid(row=1, column=0, padx=10, pady=5, sticky="e")

    devices = ["auto", "cpu", "cuda"]
    device_dropdown = ttk.Combobox(settings_window, values=devices, textvariable=app_settings.device_var)
    device_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    label_compute_type = tk.Label(settings_window, text="Compute Type:")
    label_compute_type.grid(row=2, column=0, padx=10, pady=5, sticky="e")

    compute_types = ["int8", "float16"]
    compute_type_dropdown = ttk.Combobox(settings_window, values=compute_types, textvariable=app_settings.compute_type_var)
    compute_type_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    def save_settings():
        app_settings.save_settings("settings.json")

    # automatically save settings
    app_settings.model_var.trace_add("write", lambda *args: save_settings())
    app_settings.device_var.trace_add("write", lambda *args: save_settings())
    app_settings.compute_type_var.trace_add("write", lambda *args: save_settings())

