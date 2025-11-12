# core/costeo/reportes/analisis_gastos.py
import pandas as pd
import os

def generar_analisis_gastos(df_consolidado):
    """
    Analiza gastos por categoría y producto.
    """
    df_gastos = df_consolidado.groupby('Producto').sum()[['Costo_Material', 'Costo_MOD', 'Costo_CIF']]
    return df_gastos

