# main.py
# main.py

from core.loader import cargar_maestros, cargar_kardex
from core.costeo.valorizacion import procesar_archivo
from core.costeo.costos_indirectos import analisis_relevancia
import os
from core.costeo.consolidado import generar_consolidado_y_excel

# 1️⃣ Cargar datos
df_materiales, df_mod, df_servicios, df_cif = cargar_maestros("Maestros.xlsx")

# 2️⃣ Generar Excel maestro
archivo = generar_consolidado_y_excel(df_materiales, df_mod, df_servicios, df_cif, "EmpresaX", 2025, ["01", "02"])
print(f"Excel generado: {archivo}")


# 1️⃣ Cargar archivos
path_maestro = "Empresas/Empresa_A/Maestros.xlsx"
path_kardex  = "Empresas/Empresa_A/Kardex.xlsx"

maestros = cargar_maestros(path_maestro)
kardex_df = cargar_kardex(path_kardex)

# 2️⃣ Procesar kardex (esto actualiza la hoja KMD en el Excel de maestros)
carpeta_salida = os.path.join("Resultados", "Empresa_A")
procesar_archivo(path_kardex, anno=2025, meses=[10, 11])

# 3️⃣ Generar análisis de relevancia directamente con el DataFrame MEC
df_mec = maestros["MEC"]
analisis_relevancia(df_mec, carpeta_salida)

