import pandas as pd
import os
from datetime import datetime

class EstadoResultados:
    def __init__(self, df_ventas, consolidado_costos, gastos_adm_ventas):
        self.df_ventas = df_ventas
        self.consolidado_costos = consolidado_costos
        self.gastos_adm_ventas = gastos_adm_ventas  # Tuple: (df_gastos_adm, df_gastos_ventas)
    
    def generar_estado(self, empresa, anno, meses):
        """Genera el estado de resultados consolidado"""
        print("📈 Generando estado de resultados...")
        
        # 1. Calcular ventas totales por OT
        ventas_por_ot = self._calcular_ventas_totales()
        
        # 2. Calcular costos totales por OT
        costos_por_ot = self._calcular_costos_totales()
        
        # 3. Calcular gastos por OT
        gastos_por_ot = self._calcular_gastos_totales()
        
        # 4. Consolidar todo
        estado_resultados = []
        
        todas_ots = set(list(ventas_por_ot.keys()) + 
                       list(costos_por_ot.keys()) + 
                       list(gastos_por_ot.keys()))
        
        for ot in todas_ots:
            ventas = ventas_por_ot.get(ot, 0)
            costo_ventas = costos_por_ot.get(ot, 0)
            gastos_adm = gastos_por_ot.get(ot, {}).get('administrativos', 0)
            gastos_ventas = gastos_por_ot.get(ot, {}).get('ventas', 0)
            
            utilidad_bruta = ventas - costo_ventas
            gastos_totales = gastos_adm + gastos_ventas
            utilidad_neta = utilidad_bruta - gastos_totales
            
            # Margenes
            margen_bruto = (utilidad_bruta / ventas * 100) if ventas > 0 else 0
            margen_neto = (utilidad_neta / ventas * 100) if ventas > 0 else 0
            
            estado_resultados.append({
                'OT': ot,
                'Ventas': ventas,
                'Costo_Ventas': costo_ventas,
                'Utilidad_Bruta': utilidad_bruta,
                'Margen_Bruto_%': margen_bruto,
                'Gastos_Administrativos': gastos_adm,
                'Gastos_Ventas': gastos_ventas,
                'Gastos_Totales': gastos_totales,
                'Utilidad_Neta': utilidad_neta,
                'Margen_Neto_%': margen_neto
            })
        
        df_estado = pd.DataFrame(estado_resultados)
        
        # Agregar totales
        totales = {
            'OT': 'TOTAL',
            'Ventas': df_estado['Ventas'].sum(),
            'Costo_Ventas': df_estado['Costo_Ventas'].sum(),
            'Utilidad_Bruta': df_estado['Utilidad_Bruta'].sum(),
            'Margen_Bruto_%': (df_estado['Utilidad_Bruta'].sum() / df_estado['Ventas'].sum() * 100) if df_estado['Ventas'].sum() > 0 else 0,
            'Gastos_Administrativos': df_estado['Gastos_Administrativos'].sum(),
            'Gastos_Ventas': df_estado['Gastos_Ventas'].sum(),
            'Gastos_Totales': df_estado['Gastos_Totales'].sum(),
            'Utilidad_Neta': df_estado['Utilidad_Neta'].sum(),
            'Margen_Neto_%': (df_estado['Utilidad_Neta'].sum() / df_estado['Ventas'].sum() * 100) if df_estado['Ventas'].sum() > 0 else 0
        }
        
        df_totales = pd.DataFrame([totales])
        df_estado_completo = pd.concat([df_estado, df_totales], ignore_index=True)
        
        return df_estado_completo
    
    def _calcular_ventas_totales(self):
        """Calcula ventas totales por OT"""
        ventas_por_ot = {}
        
        if self.df_ventas is not None and not self.df_ventas.empty:
            for _, venta in self.df_ventas.iterrows():
                ot = venta['OT']
                venta_total = venta['VV_total_S/']
                
                if ot not in ventas_por_ot:
                    ventas_por_ot[ot] = 0
                ventas_por_ot[ot] += venta_total
        
        return ventas_por_ot
    
    def _calcular_costos_totales(self):
        """Calcula costos totales por OT desde el consolidado"""
        costos_por_ot = {}
        
        if self.consolidado_costos is not None and not self.consolidado_costos.empty:
            for _, costo in self.consolidado_costos.iterrows():
                ot = costo['OT']
                costo_total = costo['Costo_Total']
                
                costos_por_ot[ot] = costo_total
        
        return costos_por_ot
    
    def _calcular_gastos_totales(self):
        """Calcula gastos totales por OT"""
        gastos_por_ot = {}
        
        df_gastos_adm, df_gastos_ventas = self.gastos_adm_ventas
        
        # Gastos administrativos
        if df_gastos_adm is not None and not df_gastos_adm.empty:
            for _, gasto in df_gastos_adm.iterrows():
                ot = gasto['OT']
                monto = gasto['Costo_Total']
                
                if ot not in gastos_por_ot:
                    gastos_por_ot[ot] = {'administrativos': 0, 'ventas': 0}
                gastos_por_ot[ot]['administrativos'] += monto
        
        # Gastos de ventas
        if df_gastos_ventas is not None and not df_gastos_ventas.empty:
            for _, gasto in df_gastos_ventas.iterrows():
                ot = gasto['OT']
                monto = gasto['Costo_Total']
                
                if ot not in gastos_por_ot:
                    gastos_por_ot[ot] = {'administrativos': 0, 'ventas': 0}
                gastos_por_ot[ot]['ventas'] += monto
        
        return gastos_por_ot
    
    def guardar_estado_resultados(self, empresa, anno, meses, output_path):
        """Guarda el estado de resultados en Excel"""
        estado = self.generar_estado(empresa, anno, meses)
        
        archivo_estado = f"{output_path}/Estado_Resultados.xlsx"
        
        with pd.ExcelWriter(archivo_estado, engine='openpyxl') as writer:
            estado.to_excel(writer, sheet_name="Estado Resultados", index=False)
            
            # Agregar análisis de rentabilidad
            analisis_rentabilidad = self._generar_analisis_rentabilidad(estado)
            analisis_rentabilidad.to_excel(writer, sheet_name="Análisis Rentabilidad", index=False)
        
        print(f"✅ Estado de resultados guardado: {archivo_estado}")
        return archivo_estado
    
    def _generar_analisis_rentabilidad(self, estado):
        """Genera análisis de rentabilidad por OT"""
        # Filtrar solo las OT (excluir total)
        ot_data = estado[estado['OT'] != 'TOTAL'].copy()
        
        analisis = {
            'Metrica': [
                'OT con Mayor Utilidad Neta',
                'OT con Menor Utilidad Neta', 
                'OT con Mejor Margen Neto',
                'OT con Peor Margen Neto',
                'Promedio Margen Neto',
                'Mediana Margen Neto'
            ],
            'Valor': [
                ot_data.loc[ot_data['Utilidad_Neta'].idxmax(), 'OT'],
                ot_data.loc[ot_data['Utilidad_Neta'].idxmin(), 'OT'],
                ot_data.loc[ot_data['Margen_Neto_%'].idxmax(), 'OT'],
                ot_data.loc[ot_data['Margen_Neto_%'].idxmin(), 'OT'],
                f"{ot_data['Margen_Neto_%'].mean():.2f}%",
                f"{ot_data['Margen_Neto_%'].median():.2f}%"
            ]
        }
        
        return pd.DataFrame(analisis)