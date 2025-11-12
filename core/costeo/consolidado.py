import pandas as pd
import os
from hoja_costeo import hoja_costeo_detallada
# costeo/consolidado.py

def consolidar_costos(df_materiales, df_mod, df_cif):
    """
    Consolida materiales, mano de obra y costos indirectos en un solo DataFrame resumido.
    """
    # Sumar costos por categoría
    resumen_materiales = df_materiales.groupby('Producto', as_index=False)['Costo'].sum()
    resumen_mod = df_mod.groupby('Producto', as_index=False)['Costo'].sum()
    resumen_cif = df_cif.groupby('Producto', as_index=False)['Costo'].sum()

    # Merge por Producto
    df_consolidado = resumen_materiales.merge(resumen_mod, on='Producto', how='outer', suffixes=('_Material', '_MOD'))
    df_consolidado = df_consolidado.merge(resumen_cif, on='Producto', how='outer')
    df_consolidado.rename(columns={'Costo': 'Costo_CIF'}, inplace=True)

    # Calcular costo total
    df_consolidado['Costo_Total'] = df_consolidado['Costo_Material'].fillna(0) + df_consolidado['Costo_MOD'].fillna(0) + df_consolidado['Costo_CIF'].fillna(0)

    return df_consolidado


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

