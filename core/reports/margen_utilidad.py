# core/costeo/reportes/margen_utilidad.py
import pandas as pd
import os

def generar_margen_utilidad(df_estado):
    """
    Margen de utilidad por producto.
    """
    df_margen = df_estado.copy()
    df_margen['Margen'] = df_margen['Utilidad_Bruta'] / df_margen['Monto_Venta'].replace({0:1})
    return df_margen

