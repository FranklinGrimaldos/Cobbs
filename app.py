import streamlit as st
import pandas as pd
from io import BytesIO

from src.preprocessing import prepare_zone_data, extract_well_variables
from src.models import aplicar_modelo
from src.utils import plot_caudales

st.set_page_config(page_title="Modelo Cobbs", layout="wide")

st.title("🛢️ Modelo de Inyección - Cobbs")

# 🔐 Protección básica
password = st.sidebar.text_input("Password", type="password")

if password != "cobbs123":
    st.warning("Acceso restringido")
    st.stop()
    
def dataframe_to_excel_bytes(df: pd.DataFrame) -> BytesIO:
    """
    Convierte un DataFrame a un archivo Excel en memoria.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    output.seek(0)
    return output


def leer_survey(uploaded_survey):
    """
    Lee el archivo de survey.
    Intenta primero con Hoja1; si falla, usa la primera hoja.
    """
    if uploaded_survey is None:
        return pd.DataFrame()

    try:
        return pd.read_excel(uploaded_survey, sheet_name="Hoja1")
    except Exception:
        uploaded_survey.seek(0)
        return pd.read_excel(uploaded_survey)


# -------------------------------
# Upload de archivos
# -------------------------------
st.sidebar.header("📂 Cargar datos")

uploaded_main = st.sidebar.file_uploader(
    "Archivo principal (Data_pozos.xlsx)",
    type=["xlsx"]
)

uploaded_survey = st.sidebar.file_uploader(
    "Archivo surveys (opcional)",
    type=["xlsx"]
)

ejecutar = st.sidebar.button("🚀 Ejecutar modelo")

# -------------------------------
# Botón ejecutar
# -------------------------------
if ejecutar:

    if uploaded_main is None:
        st.error("Debes cargar el archivo principal")
        st.stop()

    try:
        # Leer archivos desde Streamlit
        df = pd.read_excel(uploaded_main)
        df_survey = leer_survey(uploaded_survey)

        # -------------------------------
        # Procesamiento
        # -------------------------------
        with st.spinner("Procesando datos..."):
            df_pozo, df_zonas = prepare_zone_data(df, df_survey)
            params = extract_well_variables(df_pozo)
            res = aplicar_modelo(df_zonas, params)

        st.success("Modelo ejecutado correctamente")

        # -------------------------------
        # Mostrar resultados
        # -------------------------------
        st.subheader("📊 Resultados")
        st.dataframe(res, use_container_width=True)

        # -------------------------------
        # Gráfico
        # -------------------------------
        st.subheader("📈 Comparación de Caudales")
        fig = plot_caudales(res, pozo=params["pozo"])
        st.pyplot(fig, use_container_width=True)

        # -------------------------------
        # Descargar resultados
        # -------------------------------
        st.subheader("💾 Descargar resultados")

        excel_buffer = dataframe_to_excel_bytes(res)

        st.download_button(
            label="Descargar Excel",
            data=excel_buffer,
            file_name=f"resultado_{params['pozo']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("Ocurrió un error al ejecutar el modelo")
        st.exception(e)

else:
    st.info("Carga el archivo principal y, si quieres, el survey. Luego presiona 'Ejecutar modelo'.")