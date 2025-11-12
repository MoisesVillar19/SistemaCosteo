import pandas as pd
import os
from hoja_costeo import hoja_costeo_detallada

def generar_consolidado_y_excel(df_materiales, df_mod, df_servicios, df_cif, empresa, anno, meses):
    # 1️⃣ Consolidado resumido
    df_consolidado = consolidar_costos(df_materiales, df_mod, df_cif)

    # 2️⃣ Hoja de costeo detallada
    df_hoja = hoja_costeo_detallada(df_materiales, df_mod, df_servicios, df_cif)

    # 3️⃣ Carpeta de salida
    carpeta_salida = os.path.join("Resultados", f"{empresa}_{anno}_{'-'.join(map(str, meses))}")
    os.makedirs(carpeta_salida, exist_ok=True)

    # 4️⃣ Crear Excel con varias hojas
    archivo_excel = os.path.join(carpeta_salida, "Costeo_Empresa.xlsx")
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        df_materiales.to_excel(writer, sheet_name="Costeo Materiales", index=False)
        df_mod.to_excel(writer, sheet_name="Costeo MOD", index=False)
        df_servicios.to_excel(writer, sheet_name="Costeo Servicios", index=False)
        df_cif.to_excel(writer, sheet_name="Costos Indirectos", index=False)
        df_consolidado.to_excel(writer, sheet_name="Consolidado", index=False)
        df_hoja.to_excel(writer, sheet_name="Hoja de Costeo", index=False)

    return archivo_excel

