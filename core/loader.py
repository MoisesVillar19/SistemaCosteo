# loader.py
import pandas as pd

def cargar_maestros(path_maestro):
    """Lee todas las hojas del archivo maestro y devuelve un diccionario con DataFrames."""
    sheets = pd.read_excel(path_maestro, sheet_name=None)
    return {
        "MEC": sheets.get("MEC"),
        "MOC": sheets.get("MOC"),
        "MCC": sheets.get("MCC"),
        "KMD": sheets.get("KMD"),
        "MPD": sheets.get("MPD"),
        "MMD": sheets.get("MMD"),
        "MSD": sheets.get("MSD"),
        "IIPP": sheets.get("IIPP"),
        "VTAS": sheets.get("VTAS"),
    }

def cargar_kardex(path_kardex):
    """Lee el Kardex completo con todas las columnas necesarias."""
    columnas_necesarias = [
        "ORDEN", "ARTICULO", "NOMBRE_ITEM", "COD_ALMACEN", "ORIGEN", "NOMBRE_LARGO",
        "ANNO_MOVI", "MES_MOVI", "UNIDAD_MEDIDA", "FECHA_MOVI",
        "TIPO_DOCU", "DECRI_DOCUMENTO", "NUMERO_DOCU",
        "TIPO_OPER", "DESCRB_OPER",
        "CANT_ENTRADA", "COSTO_UNIT_ENTRADA", "COSTO_TOTAL_ENTRADA",
        "CANT_SALIDA", "COSTO_UNIT_SALIDA", "COSTO_TOTAL_SALIDA",
        "CANT_SALDO", "COSTO_UNIT_SALDO", "COSTO_TOTAL_SALDO"
    ]

    df = pd.read_excel(path_kardex)
    faltantes = [col for col in columnas_necesarias if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan las siguientes columnas en el Kardex: {faltantes}")

    # Asegurar formato de fecha
    df["FECHA_MOVI"] = pd.to_datetime(df["FECHA_MOVI"], errors="coerce")

    return df
