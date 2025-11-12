import pandas as pd

def hoja_costeo_detallada(df_materiales, df_mod, df_servicios, df_cif):
    # Agregar columna Tipo
    df_materiales['Tipo'] = 'Material'
    df_mod['Tipo'] = 'MOD'
    df_servicios['Tipo'] = 'Servicio'
    df_cif['Tipo'] = 'CIF'

    # Concatenar todos los detalles
    df_hoja = pd.concat([df_materiales, df_mod, df_servicios, df_cif], ignore_index=True)
    # Ordenar por OT y Tipo
    df_hoja = df_hoja.sort_values(by=['OT','Tipo'])
    return df_hoja

