# gui/views/dashboard_view.py
from gui.components.chart_component import Chart
from gui.components.table_component import Table

def mostrar_dashboard_completo(parent_frame, dfs: dict):
    """
    Muestra todos los gráficos y tablas del dashboard en un frame.
    dfs: dict con DataFrames de los reportes:
        - "Gastos", "Margen", "AnalisisRelevancia",
        - "Comparativo", "EstadoResultados", "KPIs"
    """
    # Limpiar frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # ----------------- Analisis de Gastos -----------------
    if "Gastos" in dfs:
        lbl_gastos = Table(parent_frame, dfs["Gastos"], titulo="Analisis de Gastos")
        lbl_gastos.pack(fill="both", expand=True, pady=5)

    # ----------------- Comparativo Periodos -----------------
    if "Comparativo" in dfs:
        tbl_compara = Table(parent_frame, dfs["Comparativo"], titulo="Comparativo de Periodos")
        tbl_compara.pack(fill="both", expand=True, pady=5)

    # ----------------- Estado de Resultados -----------------
    if "EstadoResultados" in dfs:
        tbl_estado = Table(parent_frame, dfs["EstadoResultados"], titulo="Estado de Resultados")
        tbl_estado.pack(fill="both", expand=True, pady=5)

    # ----------------- KPIs -----------------
    if "KPIs" in dfs:
        tbl_kpis = Table(parent_frame, dfs["KPIs"], titulo="KPIs")
        tbl_kpis.pack(fill="both", expand=True, pady=5)

    # ----------------- Margen de Utilidad (Gráfico) -----------------
    if "Margen" in dfs:
        Chart(parent_frame, tipo="pie", datos=dfs["Margen"], labels="Producto", values="Margen").pack(fill="both", expand=True, pady=5)

    # ----------------- Analisis de Relevancia -----------------
    if "AnalisisRelevancia" in dfs:
        tbl_relevancia = Table(parent_frame, dfs["AnalisisRelevancia"], titulo="Analisis de Relevancia")
        tbl_relevancia.pack(fill="both", expand=True, pady=5)
