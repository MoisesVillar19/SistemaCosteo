# core/costeo/reportes/kpis.py
import pandas as pd
import os

def generar_kpis(df_estado, df_consolidado, df_vtas):
    """
    KPIs generales: Total ventas, costos, utilidad y margen.
    """
    total_ventas = df_vtas['Monto_Venta'].sum()
    total_costo = df_consolidado['Costo_Total'].sum()
    utilidad = df_estado['Utilidad_Bruta'].sum()
    margen = utilidad / total_ventas if total_ventas != 0 else 0
    df_kpis = pd.DataFrame({
        'Total_Ventas': [total_ventas],
        'Total_Costo': [total_costo],
        'Utilidad_Bruta': [utilidad],
        'Margen_Utilidad': [margen]
    })
    return df_kpis
