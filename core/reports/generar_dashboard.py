from core.loader import cargar_maestros, cargar_kardex
from core.costeo.consolidado import generar_consolidado_y_excel, hoja_costeo_detallada
from core.reports.analisis_gastos import generar_analisis_gastos
from core.reports.comparativo_periodos import generar_comparativo
from core.reports.estado_resultados import generar_estado_resultados
from core.reports.kpis import generar_kpis
from core.reports.margen_utilidad import generar_margen_utilidad
import pandas as pd
import os

def generar_excel_dashboard(path_maestro, path_kardex, empresa, anno, meses):
    # Crear carpeta de resultados
    carpeta_salida = os.path.join("Resultados", f"{empresa}_{anno}_{'-'.join(map(str, meses))}")
    os.makedirs(carpeta_salida, exist_ok=True)
    archivo_excel = os.path.join(carpeta_salida, "Dashboard.xlsx")

    # Cargar datos
    maestros = cargar_maestros(path_maestro)
    kardex = cargar_kardex(path_kardex)
    df_materiales = maestros["MMD"]
    df_mod = maestros["MOC"]
    df_servicios = maestros["MSD"]
    df_cif = maestros["MCC"]

    # Consolidado y hoja de costeo
    df_consolidado = generar_consolidado_y_excel(df_materiales, df_mod, df_servicios, df_cif,
                                                 empresa=empresa, anno=anno, meses=meses)
    df_hoja_costeo = hoja_costeo_detallada(df_materiales, df_mod, df_servicios, df_cif)

    # Generar reportes
    df_gastos = generar_analisis_gastos(df_consolidado)
    df_comparativo = generar_comparativo(kardex)
    df_estado = generar_estado_resultados(df_consolidado, maestros["VTAS"])
    df_kpis = generar_kpis(df_estado, df_consolidado, maestros["VTAS"])
    df_margen = generar_margen_utilidad(df_estado)

    # Guardar todo en un Excel
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        df_materiales.to_excel(writer, sheet_name="Costeo Materiales", index=False)
        df_mod.to_excel(writer, sheet_name="Costeo MOD", index=False)
        df_servicios.to_excel(writer, sheet_name="Costeo Servicios", index=False)
        df_cif.to_excel(writer, sheet_name="Costos Indirectos", index=False)
        df_consolidado.to_excel(writer, sheet_name="Consolidado", index=False)
        df_hoja_costeo.to_excel(writer, sheet_name="Hoja de Costeo", index=False)
        df_gastos.to_excel(writer, sheet_name="Analisis Gastos")
        df_comparativo.to_excel(writer, sheet_name="Comparativo Periodos")
        df_estado.to_excel(writer, sheet_name="Estado Resultados", index=False)
        df_kpis.to_excel(writer, sheet_name="KPIs", index=False)
        df_margen.to_excel(writer, sheet_name="Margen Utilidad", index=False)

    return archivo_excel
