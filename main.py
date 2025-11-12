# main.py
import sys
import os
from core.loader import cargar_maestros, cargar_kardex
from core.costeo.valorizacion import procesar_archivo
from core.costeo.costos_indirectos import analisis_relevancia
from core.costeo.consolidado import generar_consolidado_y_excel
from core.reports.generar_dashboard import generar_excel_dashboard
from gui.main_window import MainWindow

# ------------------------------------------------------
# 🚀 Modo GUI (si se llama con "python main.py gui")
# ------------------------------------------------------
if len(sys.argv) > 1 and sys.argv[1].lower() == "gui":
    app = MainWindow()
    app.mainloop()
    sys.exit()

# ------------------------------------------------------
# ⚙️ Modo automático (sin interfaz)
# ------------------------------------------------------
def ejecutar_costeo_completo(empresa: str, anno: int, meses_input):
    """
    Ejecuta todo el flujo de costeo y análisis de relevancia sin GUI.
    """
    print(f"\n=== INICIANDO PROCESO DE COSTEO ({empresa} - {anno}) ===")

    # Rutas base
    base_empresas = os.path.join("Empresas", empresa)
    path_maestro = os.path.join(base_empresas, "Maestros.xlsx")
    path_kardex = os.path.join(base_empresas, "Kardex.xlsx")

    # Validar existencia
    if not os.path.exists(path_maestro) or not os.path.exists(path_kardex):
        raise FileNotFoundError("No se encontraron los archivos de maestros o kardex.")

    # 1️⃣ Cargar datos
    print("Cargando archivos maestros y kardex...")
    df_maestros = cargar_maestros(path_maestro)
    df_kardex = cargar_kardex(path_kardex)

    # 2️⃣ Procesar Kardex y actualizar costos
    print("Procesando kardex y valorización...")
    if isinstance(meses_input, str) and meses_input.lower() == "anual":
        meses = list(range(1, 13))
    else:
        meses = [int(m) for m in meses_input]
    procesar_archivo(path_kardex, anno=anno, meses=meses)

    # 3️⃣ Generar Excel consolidado
    print("Generando consolidado y archivo Excel...")
    archivo_consolidado = generar_consolidado_y_excel(
        df_maestros["MMD"], df_maestros["MOC"], df_maestros["MSD"], df_maestros["MCC"],
        empresa, anno, meses
    )

    # 4️⃣ Generar dashboard y análisis de relevancia
    print("Generando dashboard y análisis de relevancia...")
    archivo_dashboard, dfs_dashboard = generar_excel_dashboard(
        path_maestro, path_kardex, empresa, anno, meses
    )

    df_mec = df_maestros.get("MEC")
    if df_mec is not None:
        analisis_relevancia(df_mec, os.path.dirname(archivo_consolidado))

    print(f"\n✅ Proceso completado exitosamente.")
    print(f"📊 Consolidado: {archivo_consolidado}")
    print(f"📈 Dashboard: {archivo_dashboard}")

# ------------------------------------------------------
# 🧭 Ejemplo de ejecución directa
# ------------------------------------------------------
if __name__ == "__main__":
    empresa = "Empresa1"
    anno = 2025
    meses = ["01", "02"]  # o "anual" para todo el año
    ejecutar_costeo_completo(empresa, anno, meses)
