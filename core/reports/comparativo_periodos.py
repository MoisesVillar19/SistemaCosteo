# core/costeo/reportes/comparativo.py
import pandas as pd
import os

def generar_comparativo(df_kardex):
    """
    Comparativo de costos por periodo.
    """
    if 'Mes' not in df_kardex.columns or 'Costo_Total' not in df_kardex.columns:
        raise ValueError("El Kardex debe tener columnas 'Mes' y 'Costo_Total'")
    df_periodos = df_kardex.groupby(['Mes', 'Producto']).sum()[['Costo_Total']].unstack(fill_value=0)
    return df_periodos

