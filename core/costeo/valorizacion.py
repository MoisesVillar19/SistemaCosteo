# core/costeo/valorizacion.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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
=======
class KardexProcessor:
    def __init__(self, df_kardex=None):
        self.df_kardex = df_kardex
        self.df_reporte_materiales = None
        self.df_reporte_operaciones = None
        
    def set_kardex_data(self, df_kardex):
        """Establece el DataFrame del kardex cargado desde loader.py"""
        self.df_kardex = df_kardex
        
        # Convertir columnas de fecha si existen
        if 'FECHA_MOVI' in self.df_kardex.columns:
            self.df_kardex['FECHA_MOVI'] = pd.to_datetime(
                self.df_kardex['FECHA_MOVI'], 
                format='%d/%m/%Y', 
                errors='coerce'
            )
        
        # Asegurar tipos de datos numéricos
        columnas_numericas = [
            'CANT_ENTRADA', 'COSTO_UNIT_ENTRADA', 'COSTO_TOTAL_ENTRADA',
            'CANT_SALIDA', 'COSTO_UNIT_SALIDA', 'COSTO_TOTAL_SALIDA',
            'CANT_SALDO', 'COSTO_UNIT_SALDO', 'COSTO_TOTAL_SALDO'
        ]
        
        for col in columnas_numericas:
            if col in self.df_kardex.columns:
                self.df_kardex[col] = pd.to_numeric(self.df_kardex[col], errors='coerce')
        
        return True, "Datos del kardex establecidos exitosamente"

    def calcular_reporte_materiales(self, fecha_inicio, fecha_fin):
        """
        Calcula el reporte por materiales
        """
        try:
            if self.df_kardex is None:
                return False, "No hay datos de kardex cargados"
            
            # Filtrar por fecha
            mask = (self.df_kardex['FECHA_MOVI'] >= fecha_inicio) & (self.df_kardex['FECHA_MOVI'] <= fecha_fin)
            df_periodo = self.df_kardex[mask].copy()
            
            if df_periodo.empty:
                return False, "No hay movimientos en el período seleccionado"
            
            # Obtener materiales únicos
            materiales = df_periodo['ARTICULO'].unique()
            resultados = []
            
            for material in materiales:
                df_material = df_periodo[df_periodo['ARTICULO'] == material].copy()
                
                # Obtener saldo inicial (último movimiento antes del período)
                df_anterior = self.df_kardex[
                    (self.df_kardex['ARTICULO'] == material) & 
                    (self.df_kardex['FECHA_MOVI'] < fecha_inicio)
                ]
                
                if not df_anterior.empty:
                    saldo_inicial = df_anterior.iloc[-1]
                    saldo_inicial_cant = saldo_inicial['CANT_SALDO']
                    saldo_inicial_costo = saldo_inicial['COSTO_TOTAL_SALDO']
                else:
                    saldo_inicial_cant = 0
                    saldo_inicial_costo = 0
                
                # Calcular movimientos totales del material
                ingresos_cant = df_material['CANT_ENTRADA'].sum()
                ingresos_costo = df_material['COSTO_TOTAL_ENTRADA'].sum()
                salidas_cant = df_material['CANT_SALIDA'].sum()
                salidas_costo = df_material['COSTO_TOTAL_SALIDA'].sum()
                
                # Calcular saldo final
                saldo_final_cant = saldo_inicial_cant + ingresos_cant - salidas_cant
                saldo_final_costo = saldo_inicial_costo + ingresos_costo - salidas_costo
                saldo_final_unit = saldo_final_costo / saldo_final_cant if saldo_final_cant > 0 else 0
                
                resultados.append({
                    'MATERIAL': material,
                    'NOMBRE_ITEM': df_material['NOMBRE_ITEM'].iloc[0] if 'NOMBRE_ITEM' in df_material.columns else material,
                    'UNIDAD_MEDIDA': df_material['UNIDAD_MEDIDA'].iloc[0] if 'UNIDAD_MEDIDA' in df_material.columns else 'UN',
                    'SALDO_INICIAL_CANT': saldo_inicial_cant,
                    'SALDO_INICIAL_COSTO': saldo_inicial_costo,
                    'INGRESOS_CANT': ingresos_cant,
                    'INGRESOS_COSTO': ingresos_costo,
                    'SALIDAS_CANT': salidas_cant,
                    'SALIDAS_COSTO': salidas_costo,
                    'SALDO_FINAL_CANT': saldo_final_cant,
                    'SALDO_FINAL_COSTO': saldo_final_costo,
                    'SALDO_FINAL_UNIT': saldo_final_unit
                })
            
            self.df_reporte_materiales = pd.DataFrame(resultados)
            self._calcular_totales_materiales()
            
            return True, "Reporte por materiales calculado exitosamente"
            
        except Exception as e:
            return False, f"Error en cálculo de reporte por materiales: {str(e)}"

    def calcular_reporte_operaciones(self, fecha_inicio, fecha_fin):
        """
        Calcula el reporte por tipo de operación
        """
        try:
            if self.df_kardex is None:
                return False, "No hay datos de kardex cargados"
            
            # Filtrar por fecha
            mask = (self.df_kardex['FECHA_MOVI'] >= fecha_inicio) & (self.df_kardex['FECHA_MOVI'] <= fecha_fin)
            df_periodo = self.df_kardex[mask].copy()
            
            if df_periodo.empty:
                return False, "No hay movimientos en el período seleccionado"
            
            # Obtener tipos de operación únicos
            tipos_operacion = df_periodo['TIPO_OPER'].unique()
            resultados = []
            
            for tipo_op in tipos_operacion:
                df_tipo = df_periodo[df_periodo['TIPO_OPER'] == tipo_op]
                
                # Calcular según tipo de operación
                if tipo_op in ['ISO', 'ITR', 'TII', 'GDE']:  # Operaciones de ingreso
                    ingresos_cant = df_tipo['CANT_ENTRADA'].sum()
                    ingresos_costo = df_tipo['COSTO_TOTAL_ENTRADA'].sum()
                    salidas_cant = 0
                    salidas_costo = 0
                else:  # Operaciones de salida
                    ingresos_cant = 0
                    ingresos_costo = 0
                    salidas_cant = df_tipo['CANT_SALIDA'].sum()
                    salidas_costo = df_tipo['COSTO_TOTAL_SALIDA'].sum()
                
                # Contar número de movimientos
                num_movimientos = len(df_tipo)
                
                resultados.append({
                    'TIPO_OPERACION': tipo_op,
                    'DESCRIPCION_OPERACION': self._get_descripcion_operacion(tipo_op),
                    'NUMERO_MOVIMIENTOS': num_movimientos,
                    'INGRESOS_CANT': ingresos_cant,
                    'INGRESOS_COSTO': ingresos_costo,
                    'SALIDAS_CANT': salidas_cant,
                    'SALIDAS_COSTO': salidas_costo
                })
            
            self.df_reporte_operaciones = pd.DataFrame(resultados)
            self._calcular_totales_operaciones()
            
            return True, "Reporte por operaciones calculado exitosamente"
            
        except Exception as e:
            return False, f"Error en cálculo de reporte por operaciones: {str(e)}"

    def _calcular_totales_materiales(self):
        """Calcula los totales generales para materiales"""
        if self.df_reporte_materiales is not None:
            self.totales_materiales = {
                'SALDO_INICIAL_CANT': self.df_reporte_materiales['SALDO_INICIAL_CANT'].sum(),
                'SALDO_INICIAL_COSTO': self.df_reporte_materiales['SALDO_INICIAL_COSTO'].sum(),
                'INGRESOS_CANT': self.df_reporte_materiales['INGRESOS_CANT'].sum(),
                'INGRESOS_COSTO': self.df_reporte_materiales['INGRESOS_COSTO'].sum(),
                'SALIDAS_CANT': self.df_reporte_materiales['SALIDAS_CANT'].sum(),
                'SALIDAS_COSTO': self.df_reporte_materiales['SALIDAS_COSTO'].sum(),
                'SALDO_FINAL_CANT': self.df_reporte_materiales['SALDO_FINAL_CANT'].sum(),
                'SALDO_FINAL_COSTO': self.df_reporte_materiales['SALDO_FINAL_COSTO'].sum()
            }

    def _calcular_totales_operaciones(self):
        """Calcula los totales generales para operaciones"""
        if self.df_reporte_operaciones is not None:
            self.totales_operaciones = {
                'NUMERO_MOVIMIENTOS': self.df_reporte_operaciones['NUMERO_MOVIMIENTOS'].sum(),
                'INGRESOS_CANT': self.df_reporte_operaciones['INGRESOS_CANT'].sum(),
                'INGRESOS_COSTO': self.df_reporte_operaciones['INGRESOS_COSTO'].sum(),
                'SALIDAS_CANT': self.df_reporte_operaciones['SALIDAS_CANT'].sum(),
                'SALIDAS_COSTO': self.df_reporte_operaciones['SALIDAS_COSTO'].sum()
            }

    def _get_descripcion_operacion(self, tipo_oper):
        """Obtiene la descripción de la operación basado en el tipo"""
        descripciones = {
            'ISO': 'INGRESO DIRECTO SIN ORDEN DE COMPRA',
            'ITR': 'INGRESO POR TRANSFERENCIA',
            'STR': 'SALIDA POR TRANSFERENCIA',
            'SVA': 'SALIDA MATERIAS PRIMAS',
            'TII': 'INGRESO TOMA DE INVENTARIO',
            'TIS': 'SALIDA TOMA DE INVENTARIO',
            'GDE': 'INGRESO POR DEVOLUCION DE INVENTARIO',
            'GRE': 'SALIDA POR REINGRESO DE INVENTARIO'
        }
        return descripciones.get(tipo_oper, 'OPERACIÓN NO DEFINIDA')

# Función para integración con el sistema principal
def procesar_archivo(path_kardex, anno, meses):
    """
    Función principal para procesar el archivo de kardex
    Compatible con la estructura de main.py
    """
    try:
        # Cargar kardex usando loader
        from ..loader import cargar_kardex
        df_kardex = cargar_kardex(path_kardex)
        
        # Crear sistema de kardex
        processor = KardexProcessor(df_kardex)
        
        # Definir período
        if not meses:
            fecha_inicio = datetime(anno, 1, 1)
            fecha_fin = datetime(anno, 12, 31)
        else:
            fecha_inicio = datetime(anno, min(meses), 1)
            ultimo_mes = max(meses)
            if ultimo_mes == 12:
                fecha_fin = datetime(anno, 12, 31)
            else:
                fecha_fin = datetime(anno, ultimo_mes + 1, 1) - timedelta(days=1)
        
        # Calcular reportes
        success_mat, message_mat = processor.calcular_reporte_materiales(fecha_inicio, fecha_fin)
        success_op, message_op = processor.calcular_reporte_operaciones(fecha_inicio, fecha_fin)
        
        resultados = {
            'reporte_materiales': processor.df_reporte_materiales if success_mat else None,
            'reporte_operaciones': processor.df_reporte_operaciones if success_op else None,
            'totales_materiales': processor.totales_materiales if success_mat else None,
            'totales_operaciones': processor.totales_operaciones if success_op else None,
            'mensajes': {
                'materiales': message_mat,
                'operaciones': message_op
            }
        }
        
        return True, resultados
        
    except Exception as e:
        return False, f"Error en procesamiento: {str(e)}"

