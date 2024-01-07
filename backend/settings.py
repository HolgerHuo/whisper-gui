import os, json
import tkinter as tk

# import torch # maybe not cost-effective as we don't load torch by default

def get_cpu_core_count():
    try:
        cpu_affinity = os.sched_getaffinity(0)
        core_count = len(cpu_affinity)
        return core_count
    except AttributeError:
        return os.cpu_count() or 1
    
class AppSettings:
    def __init__(self):
        self.lang_var = tk.StringVar() # to-do: make this app multilingual
        self.model_var = tk.StringVar()
        self.device_var = tk.StringVar()
        self.cpu_threads_var = tk.StringVar()
        self.download_root_var = tk.StringVar()
        self.compute_type_var = tk.StringVar()
    
        # Default settings
        self.lang_var.set('en')
        self.model_var.set('large-v2')
        self.device_var.set('auto')
        self.cpu_threads_var.set(get_cpu_core_count()) # to-do
        self.download_root_var.set('./models') # to-do
        # self.compute_type_var.set('float16' if torch.cuda.is_available() else 'int8')
        self.compute_type_var.set('int8') # can't reliably detect quantumization type, so int8 by default

    def save_settings(self, filename):
        with open(filename, 'w') as file:
            json.dump({
                'lang': self.lang_var.get(),
                'model': self.model_var.get(),
                'device': self.device_var.get(),
                'cpu_threads': self.cpu_threads_var.get(),
                'download_root': self.download_root_var.get(),
                'compute_type': self.compute_type_var.get()
            }, file)

    def load_settings(self, filename):
        try:
            with open(filename, 'r') as file:
                settings = json.load(file)
                for var in settings.keys():
                    getattr(self, var+'_var').set(settings[var])
        except:
            open(filename, 'w').close()
