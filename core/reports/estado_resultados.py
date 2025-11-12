import pandas as pd
import numpy as np
from datetime import datetime

class EstadoResultados:
    def __init__(self, df_ventas, df_consolidado, gastos_adm_ventas):
        self.df_ventas = df_ventas
        self.df_consolidado = df_consolidado
        self.gastos_adm_ventas = gastos_adm_ventas
    
    def generar_estado_por_ot(self, empresa, anno, meses):
        """Genera estado de resultados con la estructura de la imagen"""
        print("📈 Generando estado de resultados por OT...")
        
        # 1. Calcular ventas por OT
        ventas_por_ot = self._calcular_ventas_detalladas()
        
        # 2. Calcular costos por OT
        costos_por_ot = self._calcular_costos_detallados()
        
        # 3. Calcular gastos por OT
        gastos_por_ot = self._calcular_gastos_detallados()
        
        # 4. Consolidar en formato de la imagen
        estado = self._formatear_estado_resultados(ventas_por_ot, costos_por_ot, gastos_por_ot)
        
        return estado
    
    def _calcular_ventas_detalladas(self):
        """Calcula ventas detalladas por OT"""
        ventas_detalladas = {}
        
        if self.df_ventas is not None and not self.df_ventas.empty:
            for _, venta in self.df_ventas.iterrows():
                ot = venta['OT']
                unidades = venta['Unid_vendidas']
                vv_unitario = venta['VV_unit_S/']
                vv_total = venta['VV_total_S/']
                
                if ot not in ventas_detalladas:
                    ventas_detalladas[ot] = {
                        'unidades_vendidas': 0,
                        'vv_unitario_promedio': 0,
                        'venta_total': 0,
                        'contador_ventas': 0
                    }
                
                ventas_detalladas[ot]['unidades_vendidas'] += unidades
                ventas_detalladas[ot]['venta_total'] += vv_total
                ventas_detalladas[ot]['contador_ventas'] += 1
            
            # Calcular promedio ponderado del valor de venta unitario
            for ot, datos in ventas_detalladas.items():
                if datos['unidades_vendidas'] > 0:
                    datos['vv_unitario_promedio'] = datos['venta_total'] / datos['unidades_vendidas']
        
        return ventas_detalladas
    
    def _calcular_costos_detallados(self):
        """Calcula costos detallados por OT"""
        costos_detallados = {}
        
        if self.df_consolidado is not None and not self.df_consolidado.empty:
            # Obtener datos del consolidado
            for _, consolidado in self.df_consolidado.iterrows():
                ot = consolidado['OT']
                costo_total = consolidado.get('Costo_Total', 0)
                
                # Buscar información de unidades desde ventas
                unidades_vendidas = self._obtener_unidades_ot(ot)
                
                if unidades_vendidas > 0:
                    costo_unitario = costo_total / unidades_vendidas
                else:
                    costo_unitario = 0
                
                costos_detallados[ot] = {
                    'costo_unitario': costo_unitario,
                    'costo_ventas': costo_total,
                    'costo_unitario_integral': 0,  # Se calculará después
                    'costo_total_integral': 0      # Se calculará después
                }
        
        return costos_detallados
    
    def _calcular_gastos_detallados(self):
        """Calcula gastos detallados por OT"""
        gastos_detallados = {}
        
        df_gastos_adm, df_gastos_ventas = self.gastos_adm_ventas
        
        # Procesar gastos administrativos
        if df_gastos_adm is not None and not df_gastos_adm.empty:
            for _, gasto in df_gastos_adm.iterrows():
                ot = gasto['OT']
                monto = gasto['Costo_Total']
                unidades = self._obtener_unidades_ot(ot)
                
                if ot not in gastos_detallados:
                    gastos_detallados[ot] = {'gastos_adm': 0, 'gastos_ventas': 0}
                
                gastos_detallados[ot]['gastos_adm'] += monto
        
        # Procesar gastos de ventas
        if df_gastos_ventas is not None and not df_gastos_ventas.empty:
            for _, gasto in df_gastos_ventas.iterrows():
                ot = gasto['OT']
                monto = gasto['Costo_Total']
                unidades = self._obtener_unidades_ot(ot)
                
                if ot not in gastos_detallados:
                    gastos_detallados[ot] = {'gastos_adm': 0, 'gastos_ventas': 0}
                
                gastos_detallados[ot]['gastos_ventas'] += monto
        
        return gastos_detallados
    
    def _obtener_unidades_ot(self, ot):
        """Obtiene unidades vendidas para una OT"""
        if self.df_ventas is not None and not self.df_ventas.empty:
            ventas_ot = self.df_ventas[self.df_ventas['OT'] == ot]
            return ventas_ot['Unid_vendidas'].sum()
        return 0
    
    def _formatear_estado_resultados(self, ventas_por_ot, costos_por_ot, gastos_por_ot):
        """Formatea el estado de resultados según la estructura de la imagen"""
        
        # Crear DataFrame con la estructura de la imagen
        elementos = [
            'Ventas Unidades',
            'Valor venta unitario S/',
            'Venta Total S/',
            'Costo Unitario S/',
            'Costo Ventas S/',
            'Margen Bruto S/',
            'Margen Bruto %/',
            'Costo Unitario Integral S/',
            'Costo Total Integral S/',
            'Margen Bruto Integral S/',
            'Margen Integral %'
        ]
        
        # Obtener todas las OTs únicas
        todas_ots = set(list(ventas_por_ot.keys()) + 
                       list(costos_por_ot.keys()) + 
                       list(gastos_por_ot.keys()))
        
        # Crear DataFrame vacío
        df_estado = pd.DataFrame(index=elementos, columns=list(todas_ots))
        
        # Llenar datos para cada OT
        for ot in todas_ots:
            ventas = ventas_por_ot.get(ot, {})
            costos = costos_por_ot.get(ot, {})
            gastos = gastos_por_ot.get(ot, {})
            
            # Datos de ventas
            unidades_vendidas = ventas.get('unidades_vendidas', 0)
            vv_unitario = ventas.get('vv_unitario_promedio', 0)
            venta_total = ventas.get('venta_total', 0)
            
            # Datos de costos
            costo_unitario = costos.get('costo_unitario', 0)
            costo_ventas = costos.get('costo_ventas', 0)
            
            # Cálculo de márgenes
            margen_bruto = venta_total - costo_ventas
            margen_bruto_pct = (margen_bruto / venta_total * 100) if venta_total > 0 else 0
            
            # Cálculo de costos integrales (incluyen gastos)
            gastos_totales = gastos.get('gastos_adm', 0) + gastos.get('gastos_ventas', 0)
            costo_total_integral = costo_ventas + gastos_totales
            costo_unitario_integral = costo_total_integral / unidades_vendidas if unidades_vendidas > 0 else 0
            
            margen_bruto_integral = venta_total - costo_total_integral
            margen_integral_pct = (margen_bruto_integral / venta_total * 100) if venta_total > 0 else 0
            
            # Asignar valores al DataFrame
            df_estado.loc['Ventas Unidades', ot] = unidades_vendidas
            df_estado.loc['Valor venta unitario S/', ot] = round(vv_unitario, 2)
            df_estado.loc['Venta Total S/', ot] = round(venta_total, 2)
            df_estado.loc['Costo Unitario S/', ot] = round(costo_unitario, 2)
            df_estado.loc['Costo Ventas S/', ot] = round(costo_ventas, 2)
            df_estado.loc['Margen Bruto S/', ot] = round(margen_bruto, 2)
            df_estado.loc['Margen Bruto %/', ot] = round(margen_bruto_pct, 2)
            df_estado.loc['Costo Unitario Integral S/', ot] = round(costo_unitario_integral, 2)
            df_estado.loc['Costo Total Integral S/', ot] = round(costo_total_integral, 2)
            df_estado.loc['Margen Bruto Integral S/', ot] = round(margen_bruto_integral, 2)
            df_estado.loc['Margen Integral %', ot] = round(margen_integral_pct, 2)
        
        return df_estado
    
    def guardar_estado_resultados(self, empresa, anno, meses, output_path):
        """Guarda el estado de resultados en Excel"""
        estado = self.generar_estado_por_ot(empresa, anno, meses)
        
        archivo_estado = f"{output_path}/Estado_Resultados_OT.xlsx"
        
        with pd.ExcelWriter(archivo_estado, engine='openpyxl') as writer:
            estado.to_excel(writer, sheet_name="Estado Resultados OT", index=True)
            
            # Agregar metadatos de las OTs (producto, cliente, fecha)
            metadatos_ots = self._generar_metadatos_ots()
            metadatos_ots.to_excel(writer, sheet_name="Metadatos OTs", index=False)
        
        print(f"✅ Estado de resultados por OT guardado: {archivo_estado}")
        return archivo_estado
    
    def _generar_metadatos_ots(self):
        """Genera metadatos de las OTs (producto, cliente, fecha)"""
        metadatos = []
        
        # Obtener OTs únicas
        if self.df_ventas is not None and not self.df_ventas.empty:
            ots_unicas = self.df_ventas['OT'].unique()
            
            for ot in ots_unicas:
                # Buscar información de la OT en ventas
                ot_data = self.df_ventas[self.df_ventas['OT'] == ot].iloc[0]
                
                metadatos.append({
                    'OT': ot,
                    'Descripción': ot_data.get('Descripción', ''),
                    'Cliente': ot_data.get('Cliente', ''),
                    'Fecha_Venta': ot_data.get('Fecha_venta', ''),
                    'Fecha_Fin_Producción': ot_data.get('Ffin_producción', '')
                })
        
        return pd.DataFrame(metadatos)

# Función de compatibilidad (mantener para otros archivos)
def generar_estado_resultados(df_consolidado, df_vtas):
    """
    Estado de resultados por producto (versión original - mantener compatibilidad)
    """
    if df_vtas is not None and not df_vtas.empty:
        df_ventas = df_vtas.groupby('Producto').sum()[['VV_total_S/']]
        df_ventas.rename(columns={'VV_total_S/': 'Monto_Venta'}, inplace=True)
    else:
        df_ventas = pd.DataFrame(columns=['Producto', 'Monto_Venta'])
    
    if df_consolidado is not None and not df_consolidado.empty:
        df_estado = df_ventas.merge(
            df_consolidado[['Producto','Costo_Total']], 
            on='Producto', 
            how='left'
        )
        df_estado['Utilidad_Bruta'] = df_estado['Monto_Venta'] - df_estado['Costo_Total']
    else:
        df_estado = df_ventas.copy()
        df_estado['Costo_Total'] = 0
        df_estado['Utilidad_Bruta'] = df_estado['Monto_Venta']
    
    return df_estado