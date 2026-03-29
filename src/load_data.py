
from pathlib import Path
import pandas as pd


def get_data_path(filename):
    """
    Construye la ruta a Data/filename
    """
    base_dir = Path(__file__).resolve().parents[1]
    return base_dir / "Data" / filename


def load_main_data(filename="Data_pozos.xlsx"):
    """
    Carga el archivo principal
    """
    path = get_data_path(filename)

    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    return pd.read_excel(path, header=0)


def load_survey_data(filename="Surveys.xlsx"):
    """
    Carga el archivo de survey
    """
    path = get_data_path(filename)
    try:
        df= pd.read_excel(path, sheet_name="Hoja1")
        return df
    except FileNotFoundError:
        print(f"ALERTA: Archivo Surveys.xlsx no encontrado")
        print(f" Se usará MD = TVD en todos los cálculos\n")
        return pd.DataFrame() # DataFrame vacío
    except Exception as e:
        print(f"ALERTA: Error cargando surveys: {e}")
        print(f"Se usará MD = TVD en todos los cálculos\n")
        return pd.DataFrame()
