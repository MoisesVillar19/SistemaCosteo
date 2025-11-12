import tkinter as tk
from gui.components.chart_component import Chart

def limpiar_frame(parent_frame):
    """Elimina todos los widgets del frame."""
    for widget in parent_frame.winfo_children():
        widget.destroy()

# ---------------- Gráficos principales ----------------
def mostrar_grafico_gastos(parent_frame, df_gastos):
    limpiar_frame(parent_frame)
    chart = Chart(parent_frame, tipo="bar", datos=df_gastos,
                  x="Producto", y=["Costo_Material","Costo_MOD","Costo_CIF"])
    chart.pack(fill="both", expand=True)

def mostrar_grafico_margen(parent_frame, df_margen):
    limpiar_frame(parent_frame)
    chart = Chart(parent_frame, tipo="pie", datos=df_margen,
                  labels="Producto", values="Margen")
    chart.pack(fill="both", expand=True)

# ---------------- Gráficos adicionales ----------------
def mostrar_grafico_comparativo(parent_frame, df_comparativo):
    limpiar_frame(parent_frame)
    chart = Chart(parent_frame, tipo="line", datos=df_comparativo,
                  x="Periodo", y=["Monto"])
    chart.pack(fill="both", expand=True)

def mostrar_grafico_estado_resultados(parent_frame, df_estado):
    limpiar_frame(parent_frame)
    chart = Chart(parent_frame, tipo="bar", datos=df_estado,
                  x="Cuenta", y=["Monto"])
    chart.pack(fill="both", expand=True)

def mostrar_grafico_kpis(parent_frame, df_kpis):
    limpiar_frame(parent_frame)
    chart = Chart(parent_frame, tipo="bar", datos=df_kpis,
                  x="Indicador", y=["Valor"])
    chart.pack(fill="both", expand=True)
