from tkinter import filedialog, messagebox
from core.loader import cargar_maestros, cargar_kardex
from core.costeo.consolidado import generar_consolidado_y_excel

def procesar_datos(path_maestro, path_kardex):
    try:
        # Cargar datos
        maestros = cargar_maestros(path_maestro)
        kardex = cargar_kardex(path_kardex)

        # Preparar DataFrames según tus categorías
        df_materiales = maestros["MMD"]
        df_mod = maestros["MOC"]
        df_servicios = maestros["MSD"]
        df_cif = maestros["MCC"]

        # Generar Excel consolidado
        archivo_salida = generar_consolidado_y_excel(
            df_materiales, df_mod, df_servicios, df_cif,
            empresa="empresa1", anno=2025, meses=[1,2,3]
        )

        messagebox.showinfo("Éxito", f"Archivo generado:\n{archivo_salida}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


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
        return

    # Llamada al proceso principal con las rutas seleccionadas
    procesar_datos(path_maestro, path_kardex)
