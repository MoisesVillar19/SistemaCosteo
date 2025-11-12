# core/costeo/reportes/estado_resultados.py
import pandas as pd
import os

def generar_estado_resultados(df_consolidado, df_vtas):
    """
    Estado de resultados por producto.
    """
    df_ventas = df_vtas.groupby('Producto').sum()[['Monto_Venta']]
    df_estado = df_ventas.merge(df_consolidado[['Producto','Costo_Total']], on='Producto', how='left')
    df_estado['Utilidad_Bruta'] = df_estado['Monto_Venta'] - df_estado['Costo_Total']
    return df_estado

