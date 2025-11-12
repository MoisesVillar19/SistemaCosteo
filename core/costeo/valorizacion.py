import pandas as pd
import os
from datetime import datetime

def procesar_archivo(path_kardex, anno, meses):
    """
    Procesa el archivo kardex para valorización de inventarios.
    
    Parámetros:
    -----------
    path_kardex : str
        Ruta al archivo Excel del kardex.
    anno : int
        Año a filtrar.
    meses : list[int]
        Lista de meses a filtrar (por ejemplo: [1, 2, 3]).
        
    Retorna:
    --------
    DataFrame con las columnas:
        ARTICULO, CANT_SALDO, COSTO_TOTAL_SALDO, COSTO_UNIT_PROMEDIO
    """
    print("📋 Procesando kardex para valorización...")
    
    try:
        # Verificar existencia del archivo
        if not os.path.exists(path_kardex):
            raise FileNotFoundError(f"No se encontró el archivo: {path_kardex}")
        
        # Cargar kardex
        df_kardex = pd.read_excel(path_kardex)
        
        # Verificar columnas requeridas
        columnas_necesarias = {'FECHA_MOVI', 'ARTICULO', 'CANT_SALDO', 'COSTO_TOTAL_SALDO'}
        if not columnas_necesarias.issubset(df_kardex.columns):
            raise ValueError(f"Faltan columnas requeridas en el archivo. Se esperaban: {columnas_necesarias}")
        
        # Convertir fechas
        df_kardex['FECHA_MOVI'] = pd.to_datetime(df_kardex['FECHA_MOVI'], errors='coerce')
        df_kardex = df_kardex.dropna(subset=['FECHA_MOVI'])
        
        # Crear columnas de año y mes
        df_kardex['ANNO'] = df_kardex['FECHA_MOVI'].dt.year
        df_kardex['MES'] = df_kardex['FECHA_MOVI'].dt.month
        
        # Filtrar por año y meses indicados
        df_filtrado = df_kardex[
            (df_kardex['ANNO'] == anno) & 
            (df_kardex['MES'].isin(meses))
        ]
        
        if df_filtrado.empty:
            print("⚠️ No se encontraron movimientos para el periodo indicado.")
            return pd.DataFrame()
        
        # Calcular promedios ponderados
        valorizacion = _calcular_promedio_ponderado(df_filtrado)
        
        print(f"✅ Kardex procesado correctamente ({len(df_filtrado)} movimientos filtrados).")
        return valorizacion
        
    except Exception as e:
        print(f"❌ Error procesando kardex: {str(e)}")
        return pd.DataFrame()

def _calcular_promedio_ponderado(df_kardex):
    """
    Calcula el costo promedio ponderado por artículo.
    
    Parámetros:
    -----------
    df_kardex : DataFrame
        Datos filtrados del kardex.
        
    Retorna:
    --------
    DataFrame con las columnas:
        ARTICULO, CANT_SALDO, COSTO_TOTAL_SALDO, COSTO_UNIT_PROMEDIO
    """
    if df_kardex.empty:
        return pd.DataFrame()
    
    # Agrupar por artículo y calcular saldos totales
    valorizacion = df_kardex.groupby('ARTICULO').agg({
        'CANT_SALDO': 'sum',
        'COSTO_TOTAL_SALDO': 'sum'
    }).reset_index()
    
    # Calcular costo unitario promedio ponderado
    valorizacion['COSTO_UNIT_PROMEDIO'] = (
        valorizacion['COSTO_TOTAL_SALDO'] / valorizacion['CANT_SALDO']
    ).round(4)
    
    return valorizacion
