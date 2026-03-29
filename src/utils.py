import pandas as pd
from pathlib import Path
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


def save_excel(df, filename="resultados.xlsx"):
    """
    Guarda resultados en carpeta outputs
    """
    base_dir = Path(__file__).resolve().parents[1]
    output_path = base_dir / "outputs" / "excel" / filename

    df.to_excel(output_path, index=False)

    print(f"Archivo guardado en: {output_path}")

def plot_caudales(df_zonas, pozo, filename=None):
    """
    Genera gráfico comparativo de caudales por unidad (barras horizontales).
    Guarda PNG en outputs/.
    """

    df = df_zonas.copy()

    # Orden
    df_plot = df.sort_values("UNIDAD", ascending=True)

    # Posiciones
    n = len(df_plot)
    bar_width = 0.15
    indices = np.arange(n)

    # Offsets
    offsets = [-1*bar_width, 0, 1*bar_width, 2*bar_width]

    # Columnas y labels
    columnas = ["q_ilt", "Qobj", "q_vrf", "qscero"]
    labels = ["Q ILT", "Q objetivo", "Q VRF", "Q sin daño"]

    # 🎨 Colores fijos (consistentes siempre)
    colores = ["steelblue", "seagreen", "red", "darkorange"]

    # Figura
    fig, ax = plt.subplots(figsize=(12, 6))

    # Barras
    for offset, col, label, color in zip(offsets, columnas, labels, colores):
        ax.barh(indices + offset, df_plot[col], bar_width, label=label, color=color)

    # Eje Y
    ax.set_yticks(indices)
    ax.set_yticklabels(df_plot["UNIDAD"])

    # Labels
    ax.set_xlabel("Caudal (bpd)")
    ax.set_ylabel("Mandril")
    ax.set_title(f"Comparación de Caudales: {pozo}")
    ax.legend(loc="best")

    # Etiquetas numéricas
    for i in range(n):
        for offset, col in zip(offsets, columnas):
            valor = df_plot.iloc[i][col]

            if valor is None or np.isnan(valor):
                continue

            ax.text(
                valor + max(df_plot[col].max()*0.01, 10),
                i + offset,
                f"{valor:.0f}",
                va="center",
                ha="left",
                fontsize=8
            )

    # Estética
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()

    return fig
