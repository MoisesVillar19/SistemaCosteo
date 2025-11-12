import pandas as pd
import os
from .materiales import CosteoMateriales
from .mano_obra import CosteoManoObra
from .servicios_directos import CosteoServiciosDirectos
from .hoja_costeo import hoja_costeo_detallada

def consolidar_costos(df_materiales, df_mod, df_servicios, df_cif):
    """
    Consolida materiales, mano de obra, servicios y costos indirectos
    """
    # Inicializar DataFrames vacíos si no existen
    if df_materiales is None or df_materiales.empty:
        df_materiales = pd.DataFrame(columns=['Producto', 'Costo_Total'])
    if df_mod is None or df_mod.empty:
        df_mod = pd.DataFrame(columns=['Producto', 'Costo_Total'])
    if df_servicios is None or df_servicios.empty:
        df_servicios = pd.DataFrame(columns=['Producto', 'Costo_Total'])
    if df_cif is None or df_cif.empty:
        df_cif = pd.DataFrame(columns=['Producto', 'Costo_Total'])

    # Sumar costos por categoría
    resumen_materiales = df_materiales.groupby('Producto', as_index=False)['Costo_Total'].sum()
    resumen_mod = df_mod.groupby('Producto', as_index=False)['Costo_Total'].sum()
    resumen_servicios = df_servicios.groupby('Producto', as_index=False)['Costo_Total'].sum()
    resumen_cif = df_cif.groupby('Producto', as_index=False)['Costo_Total'].sum()

    # Merge por Producto
    df_consolidado = resumen_materiales.merge(
        resumen_mod, on='Producto', how='outer', suffixes=('_Material', '_MOD')
    )
    df_consolidado = df_consolidado.merge(
        resumen_servicios, on='Producto', how='outer', suffixes=('', '_Servicios')
    )
    df_consolidado = df_consolidado.merge(
        resumen_cif, on='Producto', how='outer', suffixes=('', '_CIF')
    )
    
    # Renombrar columnas
    df_consolidado.rename(columns={
        'Costo_Total_Material': 'Costo_Material',
        'Costo_Total_MOD': 'Costo_MOD',
        'Costo_Total': 'Costo_Servicios',
        'Costo_Total_CIF': 'Costo_CIF'
    }, inplace=True)

    # Calcular costo total
    df_consolidado['Costo_Total'] = (
        df_consolidado['Costo_Material'].fillna(0) + 
        df_consolidado['Costo_MOD'].fillna(0) + 
        df_consolidado['Costo_Servicios'].fillna(0) + 
        df_consolidado['Costo_CIF'].fillna(0)
    )

    return df_consolidado

def generar_consolidado_y_excel(df_mmd, df_moc, df_msd, df_mcc, empresa, anno, meses):
    """
    Genera el consolidado completo y archivo Excel
    """
    # 1. Calcular costos de materiales
    costeo_materiales = CosteoMateriales(df_mmd, df_moc)
    costo_materiales_ot = costeo_materiales.calcular_costo_materiales(anno, meses)
    
    # Convertir a DataFrame
    df_materiales = pd.DataFrame({
        'OT': costo_materiales_ot.index,
        'Costo_Total': costo_materiales_ot.values
    })
    
    # Obtener descripción de productos desde MOC
    ot_descripciones = df_moc.set_index('Código')['Descripción del Producto'].to_dict()
    df_materiales['Producto'] = df_materiales['OT'].map(ot_descripciones)

    # 2. Calcular costos de servicios
    costeo_servicios = CosteoServiciosDirectos(df_msd, df_moc)
    costo_servicios_ot = costeo_servicios.calcular_costo_servicios(anno, meses)
    
    df_servicios = pd.DataFrame({
        'OT': costo_servicios_ot.index,
        'Costo_Total': costo_servicios_ot.values
    })
    df_servicios['Producto'] = df_servicios['OT'].map(ot_descripciones)

    # 3. Para MOD y CIF, crear DataFrames vacíos por ahora (se implementarán después)
    df_mod = pd.DataFrame(columns=['Producto', 'Costo_Total'])
    df_cif = pd.DataFrame(columns=['Producto', 'Costo_Total'])

    # 4. Consolidado resumido
    df_consolidado = consolidar_costos(df_materiales, df_mod, df_servicios, df_cif)

    # 5. Hoja de costeo detallada
    df_hoja = hoja_costeo_detallada(df_materiales, df_mod, df_servicios, df_cif)

    # 6. Carpeta de salida
    carpeta_salida = os.path.join("Resultados", f"{empresa}_{anno}_{'-'.join(map(str, meses))}")
    os.makedirs(carpeta_salida, exist_ok=True)

    # 7. Crear Excel con varias hojas
    archivo_excel = os.path.join(carpeta_salida, "Costeo_Consolidado.xlsx")
    
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        df_materiales.to_excel(writer, sheet_name="Costeo_Materiales", index=False)
        df_servicios.to_excel(writer, sheet_name="Costeo_Servicios", index=False)
        df_mod.to_excel(writer, sheet_name="Costeo_MOD", index=False)
        df_cif.to_excel(writer, sheet_name="Costos_Indirectos", index=False)
        df_consolidado.to_excel(writer, sheet_name="Consolidado", index=False)
        df_hoja.to_excel(writer, sheet_name="Hoja_Costeo", index=False)

    return archivo_excel