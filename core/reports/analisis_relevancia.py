# analisis_relevancia.py
import pandas as pd
import os

def analisis_relevancia(df_mec, carpeta_salida):
    """
    Genera el análisis de relevancia (partidas >10% del total de costos)
    a partir del DataFrame MEC.
    """

    columnas = ["id", "Codigo", "Descripcion", "Costo S/"]
    for col in columnas:
        if col not in df_mec.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    total_costos = df_mec["Costo S/"].sum()
    df_mec["% Participacion"] = (df_mec["Costo S/"] / total_costos) * 100
    df_mec["Relevante"] = df_mec["% Participacion"] > 10
    df_mec = df_mec.sort_values(by="% Participacion", ascending=False)

    os.makedirs(carpeta_salida, exist_ok=True)
    ruta_excel = os.path.join(carpeta_salida, "Analisis_Relevancia.xlsx")
    df_mec.to_excel(ruta_excel, index=False)

    # Versión resumida para dashboard
    resumen = df_mec[df_mec["Relevante"]][["Codigo", "Descripcion", "Costo S/", "% Participacion"]]
    resumen.to_csv(os.path.join(carpeta_salida, "Analisis_Relevancia_dashboard.csv"), index=False)

    return df_mec, resumen
