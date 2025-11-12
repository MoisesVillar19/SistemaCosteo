# loader.py
import pandas as pd
from pathlib import Path

def cargar_datos_empresa(nombre_empresa: str):
    base_path = Path("Empresas") / nombre_empresa

    if not base_path.exists():
        raise FileNotFoundError(f"No existe la carpeta de la empresa: {base_path}")

    path_kardex = base_path / "Kardex.xlsx"
    path_maestros = base_path / "Maestros.xlsx"

    if not path_kardex.exists():
        raise FileNotFoundError(f"Falta el archivo Kardex.xlsx en {base_path}")
    if not path_maestros.exists():
        raise FileNotFoundError(f"Falta el archivo Maestros.xlsx en {base_path}")

    kardex = cargar_kardex(path_kardex)
    maestros = cargar_maestros(path_maestros)

    return kardex, maestros

def cargar_maestros(path_maestro):
    sheets = pd.read_excel(path_maestro, sheet_name=None)
    return {
        "MEC": sheets.get("MEC"),
        "MEC2": sheets.get("MEC2"),
        "MEC3": sheets.get("MEC3"),
        "MEC4": sheets.get("MEC4"),
        "MEC5": sheets.get("MEC5"),
        "MOC": sheets.get("MOC"),
        "MCC": sheets.get("MCC"),
        "KMD": sheets.get("KMD"),
        "KSD": sheets.get("KSD"),  # Nueva hoja para kernel de servicios directos
        "MPD": sheets.get("MPD"),
        "MMD": sheets.get("MMD"),
        "MSD": sheets.get("MSD"),
        "IIPP": sheets.get("IIPP"),
        "VTAS": sheets.get("VTAS"),
    }

def cargar_kardex(path_kardex):
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

    df["FECHA_MOVI"] = pd.to_datetime(df["FECHA_MOVI"], errors="coerce")

    return df
    # Asegurar formato de fecha
    df["FECHA_MOVI"] = pd.to_datetime(df["FECHA_MOVI"], errors="coerce")

    return df
