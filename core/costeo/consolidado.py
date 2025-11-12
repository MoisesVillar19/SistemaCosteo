import pandas as pd
import os
from .materiales import CosteoMateriales
from .mano_obra import CosteoManoObra
from .servicios_directos import CosteoServiciosDirectos
from .costos_indirectos import CosteoIndirectos
from .gastos_adm_ventas import CosteoGastosAdmVentas
from .hoja_costeo import hoja_costeo_detallada
from ..reports.estado_resultados import EstadoResultados

def generar_consolidado_y_excel(df_maestros, empresa, anno, meses):
    """
    Genera el consolidado completo integrando todos los módulos
    """
    print("🏗️  Generando consolidado completo...")
    
    # Extraer dataframes de maestros
    df_mmd = df_maestros.get("MMD")
    df_moc = df_maestros.get("MOC") 
    df_msd = df_maestros.get("MSD")
    df_mcc = df_maestros.get("MCC")
    df_mec = df_maestros.get("MEC")
    df_mec2 = df_maestros.get("MEC2")
    df_mec3 = df_maestros.get("MEC3")
    df_mec4 = df_maestros.get("MEC4")
    df_mec5 = df_maestros.get("MEC5")
    df_mpd = df_maestros.get("MPD")
    df_ventas = df_maestros.get("VTAS")
    
    # 1. Costos de materiales
    print("📦 Calculando costos de materiales...")
    costeo_materiales = CosteoMateriales(df_mmd, df_moc)
    df_materiales = costeo_materiales.calcular_costo_materiales(anno, meses)
    
    # 2. Costos de servicios directos
    print("🔧 Calculando costos de servicios...")
    costeo_servicios = CosteoServiciosDirectos(df_msd, df_moc)
    df_servicios = costeo_servicios.calcular_costo_servicios(anno, meses)
    
    # 3. Costos de mano de obra directa
    print("👷 Calculando costos de mano de obra...")
    costeo_mano_obra = CosteoManoObra(df_mpd, df_mec4)
    costo_mano_obra_ot = costeo_mano_obra.calcular_costo_mano_obra(anno, meses)
    df_mod = pd.DataFrame({
        'OT': costo_mano_obra_ot.keys(),
        'Costo_Total': costo_mano_obra_ot.values()
    })
    ot_descripciones = df_moc.set_index('Código')['Descripción del Producto'].to_dict()
    df_mod['Producto'] = df_mod['OT'].map(ot_descripciones)
    
    # 4. Costos indirectos
    print("🏭 Calculando costos indirectos...")
    costeo_indirectos = CosteoIndirectos(df_mec, df_mec2, df_mec3, df_mec4, df_moc)
    df_cif = costeo_indirectos.calcular_costos_indirectos(anno, meses)
    
    # 5. Gastos administrativos y de ventas
    print("💰 Calculando gastos administrativos y de ventas...")
    costeo_gastos = CosteoGastosAdmVentas(df_mec5, df_moc, df_ventas)
    df_gastos_adm, df_gastos_ventas = costeo_gastos.generar_datos_consolidado(anno, meses)
    
    # 6. Consolidado de costos de producción
    df_consolidado = consolidar_costos(df_materiales, df_mod, df_servicios, df_cif)
    
    # 7. Hoja de costeo detallada
    df_hoja = hoja_costeo_detallada(df_materiales, df_mod, df_servicios, df_cif)
    
    # 8. Estado de resultados
    print("📊 Generando estado de resultados...")
    estado = EstadoResultados(df_ventas, df_consolidado, (df_gastos_adm, df_gastos_ventas))
    df_estado = estado.generar_estado(empresa, anno, meses)
    
    # 9. Carpeta de salida
    carpeta_salida = os.path.join("Resultados", f"{empresa}_{anno}_{'-'.join(map(str, meses))}")
    os.makedirs(carpeta_salida, exist_ok=True)
    
    # 10. Crear Excel con todas las hojas
    archivo_excel = os.path.join(carpeta_salida, "Costeo_Consolidado_Completo.xlsx")
    
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        df_materiales.to_excel(writer, sheet_name="Costeo_Materiales", index=False)
        df_servicios.to_excel(writer, sheet_name="Costeo_Servicios", index=False)
        df_mod.to_excel(writer, sheet_name="Costeo_MOD", index=False)
        df_cif.to_excel(writer, sheet_name="Costos_Indirectos", index=False)
        df_gastos_adm.to_excel(writer, sheet_name="Gastos_Administrativos", index=False)
        df_gastos_ventas.to_excel(writer, sheet_name="Gastos_Ventas", index=False)
        df_consolidado.to_excel(writer, sheet_name="Consolidado_Costos", index=False)
        df_hoja.to_excel(writer, sheet_name="Hoja_Costeo", index=False)
        df_estado.to_excel(writer, sheet_name="Estado_Resultados", index=False)
    
    # Guardar estado de resultados separado
    estado.guardar_estado_resultados(empresa, anno, meses, carpeta_salida)
    
    print(f"✅ Consolidado completo guardado: {archivo_excel}")
    return archivo_excel

def consolidar_costos(df_materiales, df_mod, df_cif):
    """
    Consolida materiales, mano de obra y costos indirectos en un solo DataFrame resumido.
    """
    # Sumar costos por categoría
    resumen_materiales = df_materiales.groupby('Producto', as_index=False)['Costo'].sum()
    resumen_mod = df_mod.groupby('Producto', as_index=False)['Costo'].sum()
    resumen_cif = df_cif.groupby('Producto', as_index=False)['Costo'].sum()

    # Merge por Producto
    df_consolidado = resumen_materiales.merge(resumen_mod, on='Producto', how='outer', suffixes=('_Material', '_MOD'))
    df_consolidado = df_consolidado.merge(resumen_cif, on='Producto', how='outer')
    df_consolidado.rename(columns={'Costo': 'Costo_CIF'}, inplace=True)

    # Calcular costo total
    df_consolidado['Costo_Total'] = df_consolidado['Costo_Material'].fillna(0) + df_consolidado['Costo_MOD'].fillna(0) + df_consolidado['Costo_CIF'].fillna(0)

    return df_consolidado


def generar_consolidado_y_excel(df_materiales, df_mod, df_servicios, df_cif, empresa, anno, meses):
    # 1️⃣ Consolidado resumido
    df_consolidado = consolidar_costos(df_materiales, df_mod, df_cif)

    # 2️⃣ Hoja de costeo detallada
    df_hoja = hoja_costeo_detallada(df_materiales, df_mod, df_servicios, df_cif)

    # 3️⃣ Carpeta de salida
    carpeta_salida = os.path.join("Resultados", f"{empresa}_{anno}_{'-'.join(map(str, meses))}")
    os.makedirs(carpeta_salida, exist_ok=True)

    # 4️⃣ Crear Excel con varias hojas
    archivo_excel = os.path.join(carpeta_salida, "Costeo_Empresa.xlsx")
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        df_materiales.to_excel(writer, sheet_name="Costeo Materiales", index=False)
        df_mod.to_excel(writer, sheet_name="Costeo MOD", index=False)
        df_servicios.to_excel(writer, sheet_name="Costeo Servicios", index=False)
        df_cif.to_excel(writer, sheet_name="Costos Indirectos", index=False)
        df_consolidado.to_excel(writer, sheet_name="Consolidado", index=False)
        df_hoja.to_excel(writer, sheet_name="Hoja de Costeo", index=False)

    return archivo_excel
