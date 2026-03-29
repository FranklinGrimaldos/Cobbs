
import pandas as pd
from scipy.interpolate import interp1d
import numpy as np

def split_main_data(df):
    """
    Separa el archivo principal en:
    - df_pozo: primeras 2 columnas
    - df_zonas: columnas restantes
    """
    df_pozo = df.iloc[:, :2].copy().dropna()
    df_zonas = df.iloc[:, 2:].copy().dropna(how="all")
    
    return df_pozo, df_zonas

def ensure_porosity(df_zonas, default_porosity=0.20):
    """
    Garantiza que exista la columna 'Porosidad'
    y llena valores faltantes
    """
    df = df_zonas.copy()

    if "porosidad" not in df.columns:
        df["porosidad"] = default_porosity
    else:
        df["porosidad"] = df["porosidad"].fillna(default_porosity)

    return df

def prepare_q_vrf(df_zonas):
    """
    Limpia y transforma la columna Q VRF:
    - Guarda etiquetas originales
    - Convierte 'FO' a 3000
    - Convierte a numérico
    """
    df = df_zonas.copy()

    # Guardar etiquetas originales
    df["labels"] = df["q_vrf"].astype(str)

    # Reemplazar FO
    df.loc[df["labels"] == "FO", "q_vrf"] = 3000

    # Convertir a numérico
    df["q_vrf"] = pd.to_numeric(df["q_vrf"], errors="coerce")

    return df

def extract_well_variables(df_pozo):
    """
    Extrae variables del pozo desde df_pozo y las devuelve en un diccionario
    """

    df = df_pozo.copy()

    # Asegurar nombres estándar
    df.columns = ["Variable", "Valor"]

    # Convertir a diccionario
    variables = pd.Series(df["Valor"].values, index=df["Variable"]).to_dict()

    # Extraer variables clave
    pattern_area = pd.to_numeric(variables.get("Pattern_Area"), errors="coerce")

    # Calcular radio equivalente del pozo
    if pd.notna(pattern_area):
        d_pozo = ((pattern_area * 43560.1742) ** 0.5) / 2
    else:
        d_pozo = 400

    # Armar diccionario final
    params = {
        "pozo": df["Valor"].iloc[0],
        "Pattern_Area": pattern_area,
        "d_pozo": d_pozo,
        "rw": pd.to_numeric(variables.get("Rw"), errors="coerce"),
        "mu": pd.to_numeric(variables.get("Visc"), errors="coerce"),
        "grad_f": pd.to_numeric(variables.get("Grad_fract"), errors="coerce"),
        "p_iny": pd.to_numeric(variables.get("Pinj"), errors="coerce"),
        "q_inj": pd.to_numeric(variables.get("Qinj"), errors="coerce"),
        "p_inj_max": pd.to_numeric(variables.get("Pinj_max"), errors="coerce"),
    }

    return params

def interpolate_md_to_tvd(md_value, df_survey):
    """
    Convierte MD a TVD usando interpolación del survey.
    
    Si no hay survey, retorna MD (fallback).
    """

    # Si no hay survey → usar MD como TVD
    if df_survey is None or df_survey.empty:
        return md_value

    try:
        # Asegurar columnas necesarias
        required_cols = {"MD", "TVD"}
        if not required_cols.issubset(df_survey.columns):
            return md_value

        # Limpiar datos
        df = df_survey.copy()
        df["MD"] = pd.to_numeric(df["MD"], errors="coerce")
        df["TVD"] = pd.to_numeric(df["TVD"], errors="coerce")
        df = df.dropna(subset=["MD", "TVD"]).sort_values("MD")

        # Crear función de interpolación
        f = interp1d(
            df["MD"],
            df["TVD"],
            kind="linear",
            fill_value="extrapolate"
        )

        return float(f(md_value))

    except Exception:
        return md_value
    
def normalize_columns(df_zonas):
    """
    Renombra columnas a formato limpio y consistente
    """

    df = df_zonas.copy()

    rename_map = {
        "K (md)": "k_md",
        "h, ft": "h_ft",
        "Q VRF": "q_vrf",
        "Q ILT": "q_ilt",
        "P ILT": "p_ilt",
        "Tope MD": "tope_md",
        "Base MD": "base_md",
        "Porosidad": "porosidad",
        "Py":"py",
    }

    df = df.rename(columns=rename_map)

    return df

def convert_numeric_columns(df_zonas):
    """
    Convierte a numérico las columnas clave del modelo
    """
    df = df_zonas.copy()

    numeric_cols = [
        "k_md",
        "h_ft",
        "q_vrf",
        "q_ilt",
        "p_ilt",
        "tope_md",
        "base_md",
        "porosidad",
        "tvd",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def prepare_zone_data(df, df_survey):
    """
    Pipeline completo de preparación de datos de zonas
    """

    # 1. Separar
    df_pozo, df_zonas = split_main_data(df)

    # 2. Normalizar nombres
    df_zonas = normalize_columns(df_zonas)

    # 3. Limpiar y preparar
    df_zonas = prepare_q_vrf(df_zonas)
    df_zonas = ensure_porosity(df_zonas)

    # 4. TVD
    df_zonas["tope_md"] = pd.to_numeric(df_zonas["tope_md"], errors="coerce")
    df_zonas["tvd"] = df_zonas["tope_md"].apply(
    lambda md: interpolate_md_to_tvd(md, df_survey)
    )

    # 5. Convertir a numérico
    df_zonas = convert_numeric_columns(df_zonas)

    return df_pozo, df_zonas