import tkinter as tk
from tkinter import messagebox

from core.loader import cargar_maestros, cargar_kardex
from core.costeo.consolidado import generar_consolidado_y_excel

def procesar_datos(path_maestro, path_kardex):
    try:
        # Cargar datos
        maestros = cargar_maestros(path_maestro)
        kardex = cargar_kardex(path_kardex)

        # Aquí llamas a tus funciones de cálculo (simulado)
        df_materiales = maestros["MMD"]
        df_mod = maestros["MOC"]
        df_servicios = maestros["MSD"]
        df_cif = maestros["MCC"]

        # Llamar a la generación del Excel final
        archivo_salida = generar_consolidado_y_excel(
            df_materiales, df_mod, df_servicios, df_cif,
            empresa="empresa1", anno=2025, meses=[1,2,3]
        )

        messagebox.showinfo("Éxito", f"Archivo generado:\n{archivo_salida}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

