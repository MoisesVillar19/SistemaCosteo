from gui.components.alert_component import mostrar_info, mostrar_error
from core.reports.generar_dashboard import generar_excel_dashboard

def ejecutar_costeo(path_maestro, path_kardex, empresa, anno, meses):
    if not path_maestro or not path_kardex:
        mostrar_error("Archivos no seleccionados")
        return None, None

    try:
        archivo_salida, dfs = generar_excel_dashboard(path_maestro, path_kardex, empresa, anno, meses)
        mostrar_info(f"Archivo generado:\n{archivo_salida}")
        return archivo_salida, dfs
    except Exception as e:
        mostrar_error(str(e))
        return None, None
