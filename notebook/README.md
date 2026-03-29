🛢️ Modelo de Inyección – Cobbs + Diagnóstico por Zona

Modelo para análisis de inyección por mandril/unidad basado en ecuación de Cobbs, integración petrofísica (R35) y lógica operativa para diagnóstico automático.

🚀 Objetivo

Automatizar el análisis de desempeño de inyección por zona, permitiendo:

Calcular caudal sin daño (QScero)
Estimar skin real (S_real)
Evaluar cumplimiento de objetivos
Diagnosticar problemas operativos (VRF, mandriles, formación)
Clasificar calidad de roca (R35)
Generar reportes y visualizaciones
🧠 Fundamento técnico
Flujo radial (base física)

Basado en formulaciones de Darcy para flujo radial en unidades de campo.

Ecuación de Cobbs

Se usa para estimar caudal de inyección:

q = 0.00354 * k * h * ΔP / (μ * (ln(d/rw) - 0.619 + s))

Donde:

k: permeabilidad (mD)
h: espesor (ft)
μ: viscosidad (cP)
ΔP: diferencial de presión (psi)
d: radio externo equivalente
rw: radio del pozo
s: skin
R35 (Winland)

Indicador de tamaño de garganta de poro:

R35 = 10^(c1 + c2log10(k) - c3log10(φ)) * 2

Permite clasificar calidad del reservorio.

📂 Estructura del proyecto
CHOQUES/
├── data/                # Datos de entrada
├── notebooks/          # Exploración y pruebas
├── outputs/            # Resultados (excel, figuras)
├── src/
│   ├── load_data.py    # Carga de datos
│   ├── preprocessing.py# Limpieza y transformación
│   ├── models.py       # Modelo físico + diagnóstico
│   └── utils.py        # Exportes y gráficos
├── app.py              # (futuro) app Streamlit
└── README.md
⚙️ Flujo del modelo
Carga de datos
Preprocesamiento:
Normalización de columnas
Cálculo TVD
Limpieza de variables
Modelo:
BHP por zona
ΔP efectivo
QScero (sin daño)
Skin real
R35
Diagnóstico:
Cumplimiento de objetivo
Diagnóstico corto operativo
Visualización y exporte