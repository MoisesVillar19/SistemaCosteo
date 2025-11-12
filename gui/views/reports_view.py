import tkinter as tk
from gui.components.table_component import Table

def limpiar_frame(parent_frame):
    """Elimina todos los widgets del frame."""
    for widget in parent_frame.winfo_children():
        widget.destroy()

def mostrar_reporte(parent_frame, df, titulo="Reporte"):
    limpiar_frame(parent_frame)
    tabla = Table(parent_frame, df, titulo=titulo)
    tabla.pack(fill="both", expand=True)

# ---------------- Funciones específicas por reporte ----------------
def mostrar_hoja_costeo(parent_frame, df):
    mostrar_reporte(parent_frame, df, "Hoja de Costeo")

def mostrar_consolidado(parent_frame, df):
    mostrar_reporte(parent_frame, df, "Consolidado")

def mostrar_analisis_gastos(parent_frame, df):
    mostrar_reporte(parent_frame, df, "Analisis de Gastos")

def mostrar_comparativo(parent_frame, df):
    mostrar_reporte(parent_frame, df, "Comparativo Periodos")

def mostrar_estado_resultados(parent_frame, df):
    mostrar_reporte(parent_frame, df, "Estado de Resultados")

def mostrar_kpis(parent_frame, df):
    mostrar_reporte(parent_frame, df, "KPIs")

def mostrar_margen_utilidad(parent_frame, df):
    mostrar_reporte(parent_frame, df, "Margen de Utilidad")
