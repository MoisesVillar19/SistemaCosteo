import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os

class KardexSystem:
    def __init__(self):
        self.df_kardex = None
        self.df_valorizacion_materiales = None
        self.df_valorizacion_operaciones = None
        self.archivo_actual = None
        
    def cargar_excel(self, file_path):
        """Carga el archivo Excel del kardex"""
        try:
            self.archivo_actual = file_path
            self.df_kardex = pd.read_excel(file_path)
            
            # Convertir columnas de fecha
            self.df_kardex['FECHA_MOVI'] = pd.to_datetime(self.df_kardex['FECHA_MOVI'], format='%d/%m/%Y')
            
            # Asegurar tipos de datos numéricos
            columnas_numericas = ['CANT_ENTRADA', 'COSTO_UNIT_ENTRADA', 'COSTO_TOTAL_ENTRADA',
                                 'CANT_SALIDA', 'COSTO_UNIT_SALIDA', 'COSTO_TOTAL_SALIDA',
                                 'CANT_SALDO', 'COSTO_UNIT_SALDO', 'COSTO_TOTAL_SALDO']
            
            for col in columnas_numericas:
                self.df_kardex[col] = pd.to_numeric(self.df_kardex[col], errors='coerce')
            
            return True, "Archivo cargado exitosamente"
            
        except Exception as e:
            return False, f"Error al cargar archivo: {str(e)}"
    
    def calcular_valorizacion(self, fecha_inicio, fecha_fin):
        """
        Calcula la valorización de inventarios por período
        """
        try:
            # Filtrar por fecha
            mask = (self.df_kardex['FECHA_MOVI'] >= fecha_inicio) & (self.df_kardex['FECHA_MOVI'] <= fecha_fin)
            df_periodo = self.df_kardex[mask].copy()
            
            if df_periodo.empty:
                return False, "No hay movimientos en el período seleccionado"
            
            # REPORTE 1: Por materiales (sin importar tipo de operación)
            materiales = df_periodo['ARTICULO'].unique()
            resultados_materiales = []
            
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
                
                resultados_materiales.append({
                    'MATERIAL': material,
                    'NOMBRE_ITEM': df_material['NOMBRE_ITEM'].iloc[0],
                    'SALDO_INICIAL_CANT': saldo_inicial_cant,
                    'SALDO_INICIAL_COSTO': saldo_inicial_costo,
                    'INGRESOS_CANT': ingresos_cant,
                    'INGRESOS_COSTO': ingresos_costo,
                    'SALIDAS_CANT': salidas_cant,
                    'SALIDAS_COSTO': salidas_costo,
                    'SALDO_FINAL_CANT': saldo_final_cant,
                    'SALDO_FINAL_COSTO': saldo_final_costo
                })
            
            self.df_valorizacion_materiales = pd.DataFrame(resultados_materiales)
            
            # REPORTE 2: Por tipo de operación (sin importar material)
            tipos_operacion = df_periodo['TIPO_OPER'].unique()
            resultados_operaciones = []
            
            for tipo_op in tipos_operacion:
                df_tipo = df_periodo[df_periodo['TIPO_OPER'] == tipo_op]
                
                if tipo_op in ['ISO', 'ITR', 'TII', 'GDE']:  # Ingresos
                    ingresos_cant = df_tipo['CANT_ENTRADA'].sum()
                    ingresos_costo = df_tipo['COSTO_TOTAL_ENTRADA'].sum()
                    salidas_cant = 0
                    salidas_costo = 0
                else:  # Salidas
                    ingresos_cant = 0
                    ingresos_costo = 0
                    salidas_cant = df_tipo['CANT_SALIDA'].sum()
                    salidas_costo = df_tipo['COSTO_TOTAL_SALIDA'].sum()
                
                resultados_operaciones.append({
                    'TIPO_OPERACION': tipo_op,
                    'DESCRIPCION_OPERACION': self._get_descripcion_operacion(tipo_op),
                    'INGRESOS_CANT': ingresos_cant,
                    'INGRESOS_COSTO': ingresos_costo,
                    'SALIDAS_CANT': salidas_cant,
                    'SALIDAS_COSTO': salidas_costo
                })
            
            self.df_valorizacion_operaciones = pd.DataFrame(resultados_operaciones)
            
            # Calcular totales
            self._calcular_totales()
            
            return True, "Valorización calculada exitosamente"
            
        except Exception as e:
            return False, f"Error en cálculo de valorización: {str(e)}"
    
    def _calcular_totales(self):
        """Calcula los totales generales del período"""
        if self.df_valorizacion_materiales is not None:
            self.totales = {
                'SALDO_INICIAL_CANT': self.df_valorizacion_materiales['SALDO_INICIAL_CANT'].sum(),
                'SALDO_INICIAL_COSTO': self.df_valorizacion_materiales['SALDO_INICIAL_COSTO'].sum(),
                'INGRESOS_CANT': self.df_valorizacion_materiales['INGRESOS_CANT'].sum(),
                'INGRESOS_COSTO': self.df_valorizacion_materiales['INGRESOS_COSTO'].sum(),
                'SALIDAS_CANT': self.df_valorizacion_materiales['SALIDAS_CANT'].sum(),
                'SALIDAS_COSTO': self.df_valorizacion_materiales['SALIDAS_COSTO'].sum(),
                'SALDO_FINAL_CANT': self.df_valorizacion_materiales['SALDO_FINAL_CANT'].sum(),
                'SALDO_FINAL_COSTO': self.df_valorizacion_materiales['SALDO_FINAL_COSTO'].sum()
            }
    
    def agregar_movimiento(self, tipo_operacion, articulo, cantidad, costo_unitario=None, 
                          fecha=None, documento=None, fecha_compra_devolucion=None):
        """Agrega un nuevo movimiento al kardex"""
        try:
            if fecha is None:
                fecha = datetime.now()
            
            if documento is None:
                # Generar número de documento consecutivo
                ultimo_doc = self.df_kardex['NUMERO_DOCU'].max()
                nuevo_num = int(ultimo_doc.split('-')[1]) + 1 if '-' in str(ultimo_doc) else 1000
                documento = f"0001-{nuevo_num:07d}"
            
            # Buscar información del artículo
            info_articulo = self.df_kardex[self.df_kardex['ARTICULO'] == articulo].iloc[0]
            
            # Obtener último saldo del artículo
            ultimo_mov = self.df_kardex[self.df_kardex['ARTICULO'] == articulo].iloc[-1]
            saldo_actual_cant = ultimo_mov['CANT_SALDO']
            saldo_actual_costo_unit = ultimo_mov['COSTO_UNIT_SALDO']
            saldo_actual_costo_total = ultimo_mov['COSTO_TOTAL_SALDO']
            
            nuevo_orden = self.df_kardex['ORDEN'].max() + 1
            
            # Determinar tipo de documento basado en tipo de operación
            if tipo_operacion in ['ISO', 'ITR', 'TII', 'GDE']:
                tipo_documento = 'GIN'
                descripcion_documento = 'GUIA DE INGRESO'
            else:
                tipo_documento = 'GSA'
                descripcion_documento = 'GUIA DE SALIDA'
            
            # Lógica según tipo de operación
            if tipo_operacion in ['ISO', 'ITR', 'TII']:  # Ingresos normales
                cant_entrada = cantidad
                costo_unit_entrada = costo_unitario
                costo_total_entrada = cantidad * costo_unitario
                cant_salida = 0
                costo_unit_salida = 0
                costo_total_salida = 0
                
                # Calcular nuevo saldo (método promedio)
                nueva_cant_saldo = saldo_actual_cant + cant_entrada
                nuevo_costo_total = saldo_actual_costo_total + costo_total_entrada
                nuevo_costo_unit = nuevo_costo_total / nueva_cant_saldo if nueva_cant_saldo > 0 else 0
                
            elif tipo_operacion in ['SVA', 'STR', 'TIS']:  # Salidas normales
                cant_entrada = 0
                costo_unit_entrada = 0
                costo_total_entrada = 0
                cant_salida = cantidad
                costo_unit_salida = saldo_actual_costo_unit
                costo_total_salida = cant_salida * costo_unit_salida
                
                # Calcular nuevo saldo
                nueva_cant_saldo = saldo_actual_cant - cant_salida
                nuevo_costo_total = saldo_actual_costo_total - costo_total_salida
                nuevo_costo_unit = saldo_actual_costo_unit  # Método promedio mantiene costo unitario
                
            elif tipo_operacion == 'GDE':  # Devolución (ingreso negativo)
                # Buscar costo unitario de la compra original
                if fecha_compra_devolucion:
                    compra_original = self.df_kardex[
                        (self.df_kardex['ARTICULO'] == articulo) & 
                        (self.df_kardex['FECHA_MOVI'] == fecha_compra_devolucion) &
                        (self.df_kardex['TIPO_OPER'].isin(['ISO', 'ITR', 'TII']))
                    ]
                    if not compra_original.empty:
                        costo_unit_compra = compra_original.iloc[0]['COSTO_UNIT_ENTRADA']
                    else:
                        return False, "No se encontró la compra original para la devolución"
                else:
                    costo_unit_compra = costo_unitario
                
                cant_entrada = -cantidad
                costo_unit_entrada = costo_unit_compra
                costo_total_entrada = -cantidad * costo_unit_compra
                cant_salida = 0
                costo_unit_salida = 0
                costo_total_salida = 0
                
                # Calcular nuevo saldo
                nueva_cant_saldo = saldo_actual_cant + cant_entrada
                nuevo_costo_total = saldo_actual_costo_total + costo_total_entrada
                nuevo_costo_unit = nuevo_costo_total / nueva_cant_saldo if nueva_cant_saldo > 0 else 0
                
            elif tipo_operacion == 'GRE':  # Reingreso (salida negativa)
                cant_entrada = 0
                costo_unit_entrada = 0
                costo_total_entrada = 0
                cant_salida = -cantidad
                costo_unit_salida = saldo_actual_costo_unit
                costo_total_salida = -cantidad * costo_unit_salida
                
                # Calcular nuevo saldo
                nueva_cant_saldo = saldo_actual_cant - cant_salida
                nuevo_costo_total = saldo_actual_costo_total - costo_total_salida
                nuevo_costo_unit = saldo_actual_costo_unit
            
            # Crear nuevo registro
            nuevo_registro = {
                'ORDEN': nuevo_orden,
                'ARTICULO': articulo,
                'NOMBRE_ITEM': info_articulo['NOMBRE_ITEM'],
                'COD_ALMACEN': info_articulo['COD_ALMACEN'],
                'ORIGEN': info_articulo['ORIGEN'],
                'NOMBRE_LARGO': info_articulo['NOMBRE_LARGO'],
                'ANNO_MOVI': fecha.year,
                'MES_MOVI': fecha.month,
                'UNIDAD_MEDIDA': info_articulo['UNIDAD_MEDIDA'],
                'FECHA_MOVI': fecha,
                'TIPO_DOCU': tipo_documento,
                'DECRI_DOCUMENTO': descripcion_documento,
                'NUMERO_DOCU': documento,
                'TIPO_OPER': tipo_operacion,
                'DESCRB_OPER': self._get_descripcion_operacion(tipo_operacion),
                'CANT_ENTRADA': cant_entrada,
                'COSTO_UNIT_ENTRADA': costo_unit_entrada,
                'COSTO_TOTAL_ENTRADA': costo_total_entrada,
                'CANT_SALIDA': cant_salida,
                'COSTO_UNIT_SALIDA': costo_unit_salida,
                'COSTO_TOTAL_SALIDA': costo_total_salida,
                'CANT_SALDO': nueva_cant_saldo,
                'COSTO_UNIT_SALDO': nuevo_costo_unit,
                'COSTO_TOTAL_SALDO': nuevo_costo_total
            }
            
            # Agregar nuevo registro al DataFrame
            nuevo_df = pd.DataFrame([nuevo_registro])
            self.df_kardex = pd.concat([self.df_kardex, nuevo_df], ignore_index=True)
            
            # Guardar cambios en el archivo
            self.guardar_cambios()
            
            return True, f"Movimiento agregado exitosamente. Documento: {documento}"
            
        except Exception as e:
            return False, f"Error al agregar movimiento: {str(e)}"
    
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
    
    def obtener_fechas_compra(self, articulo):
        """Obtiene las fechas de compra disponibles para un artículo (para devoluciones)"""
        if self.df_kardex is not None:
            compras = self.df_kardex[
                (self.df_kardex['ARTICULO'] == articulo) & 
                (self.df_kardex['TIPO_OPER'].isin(['ISO', 'ITR', 'TII']))
            ]
            return compras['FECHA_MOVI'].tolist()
        return []
    
    def guardar_cambios(self):
        """Guarda los cambios en el archivo Excel original"""
        if self.archivo_actual and self.df_kardex is not None:
            try:
                self.df_kardex.to_excel(self.archivo_actual, index=False)
                return True, "Cambios guardados exitosamente"
            except Exception as e:
                return False, f"Error al guardar cambios: {str(e)}"
        return False, "No hay archivo cargado"
    
    def obtener_materiales(self):
        """Retorna la lista de materiales disponibles"""
        if self.df_kardex is not None:
            return self.df_kardex[['ARTICULO', 'NOMBRE_ITEM']].drop_duplicates().values.tolist()
        return []
    
    def obtener_tipos_operacion(self):
        """Retorna los tipos de operación disponibles"""
        return ['ISO', 'ITR', 'STR', 'SVA', 'TII', 'TIS', 'GDE', 'GRE']

class KardexGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Costeo - Módulo Kardex Mejorado")
        self.root.geometry("1400x900")
        
        self.kardex_system = KardexSystem()
        self.fecha_compra_seleccionada = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña de Valorización
        self.tab_valorizacion = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_valorizacion, text="Valorización")
        
        # Pestaña de Movimientos
        self.tab_movimientos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_movimientos, text="Gestión de Movimientos")
        
        self.setup_tab_valorizacion()
        self.setup_tab_movimientos()
    
    def setup_tab_valorizacion(self):
        # Frame principal
        main_frame = ttk.Frame(self.tab_valorizacion, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Valorización de Inventarios", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sección de carga de archivo
        file_frame = ttk.LabelFrame(main_frame, text="Cargar Archivo Kardex", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Archivo:").grid(row=0, column=0, sticky='w')
        self.file_path = ttk.Entry(file_frame, width=50)
        self.file_path.grid(row=0, column=1, sticky='ew', padx=(5, 5))
        ttk.Button(file_frame, text="Examinar", command=self.cargar_archivo).grid(row=0, column=2)
        
        # Sección de parámetros
        params_frame = ttk.LabelFrame(main_frame, text="Parámetros de Valorización", padding="10")
        params_frame.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # Fechas
        ttk.Label(params_frame, text="Fecha Inicio:").grid(row=0, column=0, sticky='w')
        self.fecha_inicio = ttk.Entry(params_frame, width=15)
        self.fecha_inicio.grid(row=0, column=1, sticky='w')
        self.fecha_inicio.insert(0, "01/01/2025")
        
        ttk.Label(params_frame, text="Fecha Fin:").grid(row=0, column=2, sticky='w', padx=(20, 0))
        self.fecha_fin = ttk.Entry(params_frame, width=15)
        self.fecha_fin.grid(row=0, column=3, sticky='w')
        self.fecha_fin.insert(0, "31/12/2025")
        
        # Selección de reporte
        ttk.Label(params_frame, text="Tipo de Reporte:").grid(row=1, column=0, sticky='w', pady=(10, 0))
        self.tipo_reporte = ttk.Combobox(params_frame, values=['Por Materiales', 'Por Operaciones'], state="readonly")
        self.tipo_reporte.grid(row=1, column=1, sticky='w')
        self.tipo_reporte.set('Por Materiales')
        self.tipo_reporte.bind('<<ComboboxSelected>>', self.cambiar_reporte)
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 10))
        
        ttk.Button(button_frame, text="Calcular Valorización", 
                  command=self.calcular_valorizacion).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Exportar a Excel", 
                  command=self.exportar_excel).pack(side='left')
        
        # Área de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.grid(row=4, column=0, columnspan=3, sticky='nsew', pady=(0, 10))
        main_frame.rowconfigure(4, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview para mostrar resultados
        self.columns_materiales = ('MATERIAL', 'SALDO_INICIAL_CANT', 'SALDO_INICIAL_COSTO', 
                                  'INGRESOS_CANT', 'INGRESOS_COSTO', 'SALIDAS_CANT', 'SALIDAS_COSTO',
                                  'SALDO_FINAL_CANT', 'SALDO_FINAL_COSTO')
        
        self.columns_operaciones = ('TIPO_OPERACION', 'DESCRIPCION', 'INGRESOS_CANT', 'INGRESOS_COSTO',
                                   'SALIDAS_CANT', 'SALIDAS_COSTO')
        
        self.tree_valorizacion = ttk.Treeview(results_frame, columns=self.columns_materiales, show='headings', height=20)
        
        # Configurar columnas iniciales (materiales)
        self.configurar_columnas_materiales()
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.tree_valorizacion.yview)
        self.tree_valorizacion.configure(yscrollcommand=scrollbar.set)
        
        self.tree_valorizacion.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Frame para totales
        totales_frame = ttk.Frame(main_frame)
        totales_frame.grid(row=5, column=0, columnspan=3, sticky='ew', pady=(5, 0))
        
        self.label_totales = ttk.Label(totales_frame, text="Totales: ", font=('Arial', 10, 'bold'))
        self.label_totales.pack(side='left')
        
        # Barra de estado
        self.status_bar = ttk.Label(main_frame, text="Listo", relief='sunken', anchor='w')
        self.status_bar.grid(row=6, column=0, columnspan=3, sticky='ew')
    
    def configurar_columnas_materiales(self):
        """Configura las columnas para el reporte por materiales"""
        for col in self.tree_valorizacion['columns']:
            self.tree_valorizacion.heading(col, text=col.replace('_', ' ').title())
            self.tree_valorizacion.column(col, width=120)
    
    def configurar_columnas_operaciones(self):
        """Configura las columnas para el reporte por operaciones"""
        for col in self.tree_valorizacion['columns']:
            self.tree_valorizacion.heading(col, text=col.replace('_', ' ').title())
            self.tree_valorizacion.column(col, width=150)
    
    def cambiar_reporte(self, event=None):
        """Cambia entre reporte por materiales y por operaciones"""
        tipo = self.tipo_reporte.get()
        
        # Limpiar treeview
        for item in self.tree_valorizacion.get_children():
            self.tree_valorizacion.delete(item)
        
        if tipo == 'Por Materiales':
            self.tree_valorizacion.configure(columns=self.columns_materiales)
            self.configurar_columnas_materiales()
            if hasattr(self, 'df_materiales_actual'):
                self.mostrar_resultados_materiales()
        else:
            self.tree_valorizacion.configure(columns=self.columns_operaciones)
            self.configurar_columnas_operaciones()
            if hasattr(self, 'df_operaciones_actual'):
                self.mostrar_resultados_operaciones()
    
    def setup_tab_movimientos(self):
        # Frame principal
        main_frame = ttk.Frame(self.tab_movimientos, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Gestión de Movimientos", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Formulario para nuevo movimiento
        form_frame = ttk.LabelFrame(main_frame, text="Nuevo Movimiento", padding="10")
        form_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)
        
        # Tipo de operación
        ttk.Label(form_frame, text="Tipo Operación:").grid(row=0, column=0, sticky='w', pady=5)
        self.tipo_operacion = ttk.Combobox(form_frame, values=self.kardex_system.obtener_tipos_operacion(), state="readonly")
        self.tipo_operacion.grid(row=0, column=1, sticky='ew', pady=5, padx=(5, 0))
        self.tipo_operacion.bind('<<ComboboxSelected>>', self.on_tipo_operacion_change)
        
        # Material
        ttk.Label(form_frame, text="Material:").grid(row=1, column=0, sticky='w', pady=5)
        self.material = ttk.Combobox(form_frame, state="readonly")
        self.material.grid(row=1, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        # Cantidad
        ttk.Label(form_frame, text="Cantidad:").grid(row=2, column=0, sticky='w', pady=5)
        self.cantidad = ttk.Entry(form_frame)
        self.cantidad.grid(row=2, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        # Costo Unitario (solo para ingresos normales)
        ttk.Label(form_frame, text="Costo Unitario:").grid(row=3, column=0, sticky='w', pady=5)
        self.costo_unitario = ttk.Entry(form_frame)
        self.costo_unitario.grid(row=3, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        # Botón para seleccionar fecha de compra (solo para devoluciones)
        self.btn_seleccionar_fecha = ttk.Button(form_frame, text="Seleccionar Fecha Compra", 
                                               command=self.seleccionar_fecha_compra)
        self.btn_seleccionar_fecha.grid(row=4, column=0, columnspan=2, pady=5)
        self.btn_seleccionar_fecha.grid_remove()  # Ocultar inicialmente
        
        # Etiqueta para fecha seleccionada
        self.label_fecha_seleccionada = ttk.Label(form_frame, text="Fecha compra: No seleccionada", 
                                                 foreground="blue")
        self.label_fecha_seleccionada.grid(row=5, column=0, columnspan=2, pady=5)
        self.label_fecha_seleccionada.grid_remove()  # Ocultar inicialmente
        
        # Documento
        ttk.Label(form_frame, text="N° Documento:").grid(row=6, column=0, sticky='w', pady=5)
        self.documento = ttk.Entry(form_frame)
        self.documento.grid(row=6, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        # Botón agregar
        ttk.Button(form_frame, text="Agregar Movimiento", 
                  command=self.agregar_movimiento).grid(row=7, column=0, columnspan=2, pady=10)
        
        # Área de últimos movimientos
        movimientos_frame = ttk.LabelFrame(main_frame, text="Últimos Movimientos", padding="10")
        movimientos_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)
        movimientos_frame.columnconfigure(0, weight=1)
        movimientos_frame.rowconfigure(0, weight=1)
        
        # Treeview para movimientos
        columns_mov = ('ORDEN', 'FECHA', 'ARTICULO', 'TIPO_OPER', 'TIPO_DOCU', 'CANT_ENTRADA', 
                      'CANT_SALIDA', 'COSTO_TOTAL_ENTRADA', 'COSTO_TOTAL_SALIDA', 'CANT_SALDO')
        
        self.tree_movimientos = ttk.Treeview(movimientos_frame, columns=columns_mov, show='headings', height=15)
        
        # Configurar columnas
        for col in columns_mov:
            self.tree_movimientos.heading(col, text=col.replace('_', ' ').title())
            self.tree_movimientos.column(col, width=100)
        
        # Scrollbar
        scrollbar_mov = ttk.Scrollbar(movimientos_frame, orient='vertical', command=self.tree_movimientos.yview)
        self.tree_movimientos.configure(yscrollcommand=scrollbar_mov.set)
        
        self.tree_movimientos.grid(row=0, column=0, sticky='nsew')
        scrollbar_mov.grid(row=0, column=1, sticky='ns')
    
    def on_tipo_operacion_change(self, event):
        """Habilita/deshabilita campos según el tipo de operación"""
        tipo_op = self.tipo_operacion.get()
        
        # Limpiar campos
        self.costo_unitario.delete(0, tk.END)
        self.fecha_compra_seleccionada = None
        self.label_fecha_seleccionada.config(text="Fecha compra: No seleccionada")
        
        if tipo_op in ['ISO', 'ITR', 'TII']:  # Ingresos normales
            self.costo_unitario.config(state='normal')
            self.btn_seleccionar_fecha.grid_remove()
            self.label_fecha_seleccionada.grid_remove()
        elif tipo_op == 'GDE':  # Devolución
            self.costo_unitario.config(state='disabled')
            self.btn_seleccionar_fecha.grid()
            self.label_fecha_seleccionada.grid()
        else:  # Salidas normales y reingresos
            self.costo_unitario.config(state='disabled')
            self.btn_seleccionar_fecha.grid_remove()
            self.label_fecha_seleccionada.grid_remove()
    
    def seleccionar_fecha_compra(self):
        """Abre diálogo para seleccionar fecha de compra para devolución"""
        material = self.material.get().split(' - ')[0] if self.material.get() else None
        if not material:
            messagebox.showerror("Error", "Primero seleccione un material")
            return
        
        fechas_compras = self.kardex_system.obtener_fechas_compra(material)
        if not fechas_compras:
            messagebox.showerror("Error", "No hay compras registradas para este material")
            return
        
        # Crear ventana de selección
        seleccion_window = tk.Toplevel(self.root)
        seleccion_window.title("Seleccionar Fecha de Compra")
        seleccion_window.geometry("400x300")
        
        ttk.Label(seleccion_window, text="Seleccione la fecha de la compra original:", 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Lista de fechas
        lista_fechas = tk.Listbox(seleccion_window, height=10)
        for fecha in fechas_compras:
            lista_fechas.insert(tk.END, fecha.strftime('%d/%m/%Y'))
        lista_fechas.pack(fill='both', expand=True, padx=10, pady=5)
        
        def confirmar_seleccion():
            seleccion = lista_fechas.curselection()
            if seleccion:
                fecha_str = lista_fechas.get(seleccion[0])
                self.fecha_compra_seleccionada = datetime.strptime(fecha_str, '%d/%m/%Y')
                self.label_fecha_seleccionada.config(text=f"Fecha compra: {fecha_str}")
                seleccion_window.destroy()
            else:
                messagebox.showerror("Error", "Seleccione una fecha")
        
        ttk.Button(seleccion_window, text="Confirmar", 
                  command=confirmar_seleccion).pack(pady=10)
    
    def cargar_archivo(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Kardex",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, file_path)
            
            success, message = self.kardex_system.cargar_excel(file_path)
            self.actualizar_estado(message)
            
            if success:
                # Actualizar combobox de materiales
                materiales = self.kardex_system.obtener_materiales()
                self.material['values'] = [f"{m[0]} - {m[1]}" for m in materiales]
                
                # Cargar últimos movimientos
                self.cargar_ultimos_movimientos()
    
    def cargar_ultimos_movimientos(self):
        """Carga los últimos movimientos en el treeview"""
        if self.kardex_system.df_kardex is not None:
            # Limpiar treeview
            for item in self.tree_movimientos.get_children():
                self.tree_movimientos.delete(item)
            
            # Obtener últimos 50 movimientos
            df_ultimos = self.kardex_system.df_kardex.tail(50)
            
            for _, row in df_ultimos.iterrows():
                self.tree_movimientos.insert('', tk.END, values=(
                    row['ORDEN'],
                    row['FECHA_MOVI'].strftime('%d/%m/%Y'),
                    row['ARTICULO'],
                    row['TIPO_OPER'],
                    row['TIPO_DOCU'],
                    row['CANT_ENTRADA'],
                    row['CANT_SALIDA'],
                    f"{row['COSTO_TOTAL_ENTRADA']:,.2f}",
                    f"{row['COSTO_TOTAL_SALIDA']:,.2f}",
                    row['CANT_SALDO']
                ))
    
    def calcular_valorizacion(self):
        try:
            fecha_inicio = datetime.strptime(self.fecha_inicio.get(), "%d/%m/%Y")
            fecha_fin = datetime.strptime(self.fecha_fin.get(), "%d/%m/%Y")
            
            success, message = self.kardex_system.calcular_valorizacion(fecha_inicio, fecha_fin)
            self.actualizar_estado(message)
            
            if success:
                tipo_reporte = self.tipo_reporte.get()
                if tipo_reporte == 'Por Materiales':
                    self.mostrar_resultados_materiales()
                else:
                    self.mostrar_resultados_operaciones()
                self.mostrar_totales()
                
        except ValueError as e:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use dd/mm/yyyy")
        except Exception as e:
            messagebox.showerror("Error", f"Error en cálculo: {str(e)}")
    
    def mostrar_resultados_materiales(self):
        """Muestra resultados del reporte por materiales"""
        # Limpiar treeview
        for item in self.tree_valorizacion.get_children():
            self.tree_valorizacion.delete(item)
        
        if self.kardex_system.df_valorizacion_materiales is not None:
            self.df_materiales_actual = self.kardex_system.df_valorizacion_materiales
            for _, row in self.kardex_system.df_valorizacion_materiales.iterrows():
                self.tree_valorizacion.insert('', tk.END, values=(
                    f"{row['MATERIAL']} - {row['NOMBRE_ITEM']}",
                    f"{row['SALDO_INICIAL_CANT']:,.2f}",
                    f"{row['SALDO_INICIAL_COSTO']:,.2f}",
                    f"{row['INGRESOS_CANT']:,.2f}",
                    f"{row['INGRESOS_COSTO']:,.2f}",
                    f"{row['SALIDAS_CANT']:,.2f}",
                    f"{row['SALIDAS_COSTO']:,.2f}",
                    f"{row['SALDO_FINAL_CANT']:,.2f}",
                    f"{row['SALDO_FINAL_COSTO']:,.2f}"
                ))
    
    def mostrar_resultados_operaciones(self):
        """Muestra resultados del reporte por operaciones"""
        # Limpiar treeview
        for item in self.tree_valorizacion.get_children():
            self.tree_valorizacion.delete(item)
        
        if self.kardex_system.df_valorizacion_operaciones is not None:
            self.df_operaciones_actual = self.kardex_system.df_valorizacion_operaciones
            for _, row in self.kardex_system.df_valorizacion_operaciones.iterrows():
                self.tree_valorizacion.insert('', tk.END, values=(
                    row['TIPO_OPERACION'],
                    row['DESCRIPCION_OPERACION'],
                    f"{row['INGRESOS_CANT']:,.2f}",
                    f"{row['INGRESOS_COSTO']:,.2f}",
                    f"{row['SALIDAS_CANT']:,.2f}",
                    f"{row['SALIDAS_COSTO']:,.2f}"
                ))
    
    def mostrar_totales(self):
        """Muestra los totales generales"""
        if hasattr(self.kardex_system, 'totales'):
            totales = self.kardex_system.totales
            texto = (f"Totales - Saldo Inicial: {totales['SALDO_INICIAL_CANT']:,.0f} und / S/. {totales['SALDO_INICIAL_COSTO']:,.2f} | "
                    f"Ingresos: {totales['INGRESOS_CANT']:,.0f} und / S/. {totales['INGRESOS_COSTO']:,.2f} | "
                    f"Salidas: {totales['SALIDAS_CANT']:,.0f} und / S/. {totales['SALIDAS_COSTO']:,.2f} | "
                    f"Saldo Final: {totales['SALDO_FINAL_CANT']:,.0f} und / S/. {totales['SALDO_FINAL_COSTO']:,.2f}")
            self.label_totales.config(text=texto)
    
    def agregar_movimiento(self):
        try:
            # Validar campos
            if not self.tipo_operacion.get():
                messagebox.showerror("Error", "Seleccione el tipo de operación")
                return
            
            if not self.material.get():
                messagebox.showerror("Error", "Seleccione el material")
                return
            
            if not self.cantidad.get() or float(self.cantidad.get()) <= 0:
                messagebox.showerror("Error", "Ingrese una cantidad válida")
                return
            
            tipo_op = self.tipo_operacion.get()
            articulo = self.material.get().split(' - ')[0]
            cantidad = float(self.cantidad.get())
            costo_unitario = float(self.costo_unitario.get()) if self.costo_unitario.get() and self.costo_unitario['state'] == 'normal' else None
            documento = self.documento.get() if self.documento.get() else None
            
            # Validaciones específicas
            if tipo_op in ['ISO', 'ITR', 'TII'] and costo_unitario is None:
                messagebox.showerror("Error", "Ingrese el costo unitario para ingresos")
                return
            
            if tipo_op == 'GDE' and self.fecha_compra_seleccionada is None:
                messagebox.showerror("Error", "Seleccione la fecha de compra para la devolución")
                return
            
            success, message = self.kardex_system.agregar_movimiento(
                tipo_op, articulo, cantidad, costo_unitario, datetime.now(), 
                documento, self.fecha_compra_seleccionada
            )
            
            self.actualizar_estado(message)
            
            if success:
                # Limpiar formulario
                self.cantidad.delete(0, tk.END)
                self.costo_unitario.delete(0, tk.END)
                self.documento.delete(0, tk.END)
                self.fecha_compra_seleccionada = None
                self.label_fecha_seleccionada.config(text="Fecha compra: No seleccionada")
                
                # Actualizar lista de movimientos
                self.cargar_ultimos_movimientos()
                
                messagebox.showinfo("Éxito", message)
                
        except ValueError as e:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar movimiento: {str(e)}")
    
    def exportar_excel(self):
        if (self.kardex_system.df_valorizacion_materiales is not None and 
            self.kardex_system.df_kardex is not None):
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar reporte de valorización"
            )
            if file_path:
                try:
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        # 1. Guardar Kardex completo (con nuevos movimientos)
                        self.kardex_system.df_kardex.to_excel(writer, sheet_name='Kardex_Completo', index=False)
                        
                        # 2. Guardar reporte por materiales
                        self.kardex_system.df_valorizacion_materiales.to_excel(writer, sheet_name='Reporte_Materiales', index=False)
                        
                        # 3. Guardar reporte por operaciones
                        self.kardex_system.df_valorizacion_operaciones.to_excel(writer, sheet_name='Reporte_Operaciones', index=False)
                        
                        # 4. Guardar totales
                        totales_df = pd.DataFrame([self.kardex_system.totales])
                        totales_df.to_excel(writer, sheet_name='Totales', index=False)
                    
                    self.actualizar_estado(f"Reporte exportado exitosamente: {file_path}")
                    messagebox.showinfo("Éxito", f"Reporte exportado a:\n{file_path}")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al exportar: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Primero debe calcular la valorización")
    
    def actualizar_estado(self, mensaje):
        self.status_bar.config(text=mensaje)
        self.root.update()

def main():
    root = tk.Tk()
    app = KardexGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()