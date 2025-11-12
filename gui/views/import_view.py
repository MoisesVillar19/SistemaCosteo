# gui/views/import_view.py
from tkinter import filedialog, messagebox

def seleccionar_archivos():
    path_maestro = filedialog.askopenfilename(
        title="Seleccionar archivo de Maestros",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    path_kardex = filedialog.askopenfilename(
        title="Seleccionar archivo de Kardex",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if not path_maestro or not path_kardex:
        messagebox.showerror("Error", "Debe seleccionar ambos archivos (Maestros y Kardex).")
        return None, None
    return path_maestro, path_kardex


