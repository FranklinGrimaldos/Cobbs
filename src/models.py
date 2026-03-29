import numpy as np
import pandas as pd

def calcular_I_base(k_md, h_ft, mu, p_iny, p_yac, d, rw, s=0):
    """
    Calcula el caudal base de inyección I_base para una zona o pozo.
    
    Ecuación de Cobbs:
    I = 0.00354 * K * h * ΔP / (μ * (ln(d/rw) - 0.619 + s))
    """
    delta_p = p_iny - p_yac
    denominador = max(np.log(d / rw) - 0.619 + (s), 0.000000001)
    
    if denominador <= 0:
        return np.nan
    
    I_base = 0.00354 * k_md * h_ft * delta_p / (mu * denominador)
    return I_base

def estimar_skin(k_md, h_ft,  mu, p_iny, p_yac, d, rw, tasa_objetivo):
    """
    Estima el skin necesario para que la tasa de inyección sea igual a la observada.
    """
    delta_p = p_iny - p_yac
    if tasa_objetivo <= 0:
        return np.inf
    
    if delta_p <= 0:
        return np.nan    
    
    parte_teorica = (0.00354 * k_md * h_ft * delta_p) /max(mu * tasa_objetivo, 0.000000001)
    log_term = np.log(d / rw)
    
    s = parte_teorica - log_term + 0.619
    return s

def calcular_r35(k_md,porosidad):
    """
    Calcula la garganta de poro (R35) en micras.
    
    Fórmula: R35 = 10^(c1 + c2*log10(K) - c3*log10(Poro*100)) * 2
    """
    # Constantes para R35 (Garganta de Poro)
    c1 = 0.732
    c2 = 0.588
    c3 = 0.864
    if k_md <= 0 or porosidad <= 0:
        return np.nan
    
    try:
        poro_pct = porosidad * 100
        exponent = c1 + c2 * np.log10(k_md) - c3 * np.log10(poro_pct)
        r35 = (10 ** exponent) * 2
        return r35
    except:
        return np.nan

def clasificar_calidad_poro(r35):
    """
    Clasifica la calidad del reservorio basado en R35.
    
    Retorna: (clasificación, color, sensibilidad)
    """
    if pd.isna(r35):
        return pd.isna
    
    if r35 > 60:
        return "Excelente"
    elif r35 >= 45:
        return "Buena"
    elif r35 >= 24:
        return "Regular"
    else:
        return "Pobre"
    

def clasificar_estado_presion(del_p):
    """
    Clasifica el estado del diferencial de presión
    """

    try:
        if del_p is None or np.isnan(del_p):
            return "No disponible"

        if del_p < 0:
            return "Valor inválido"

        if del_p <= 2500:
            return "Diferencial Adecuado"
        elif del_p <= 3000:
            return f"Diferencial Alto ({del_p:.0f} psi)"
        elif del_p <= 3500:
            return f"Diferencial Crítico ({del_p:.0f} psi)"
        else:
            return f"Diferencial Severamente Crítico ({del_p:.0f} psi)"

    except Exception:
        return "No disponible"
    

def cumplimiento_objetivo(row):
    """Evalúa cumplimiento de objetivo"""
    qreal = row['q_ilt']
    Qobj = row['Qobj']
    
    if 0.8 * Qobj <= qreal <= 1.2 * Qobj:
        return "Cumpliendo", 1
    else:
        return "Incumpliendo", 0

def diagnosticar_corto(row):
    """
    Diagnóstico corto para reportes
    """
    try:
        qreal = row["q_ilt"]
        qobj = row["Qobj"]
        qscero = row["qscero"]
        qvrf = row["q_vrf"]
        label = row["labels"]

        if any(pd_val is None for pd_val in [qreal, qobj, qscero, qvrf]):
            return "SD"

        if any(np.isnan(v) for v in [qreal, qobj, qscero, qvrf]):
            return "SD"

        if qreal < qobj and qobj <= qscero and qvrf > qreal and label != "FO":
            return "Problema VRF"
        if qreal < qobj and qobj <= qscero and qvrf >= qreal and label == "FO":
            return "Daño de FM"
        if qobj > qscero and qreal < qobj:
            return "Alto Qobj"
        if qobj > qscero and qreal > qobj:
            return "Alto Qreal/ Daño Mandriles"
        if qreal > qscero and qscero > qobj:
            return "Daño Mandril/Pase entre zonas"
        if qreal > 1.2 * qobj and qreal > 1.2 * qvrf:
            return "Problema Mandril/VRF"
        if qreal > 1.2 * qobj and qreal < qvrf:
            return "Ajustar VRF"

        return "SD"

    except Exception:
        return "SD"

def aplicar_modelo(df_zonas, params):
    """
    Aplica el modelo completo por zona.
    """
    df = df_zonas.copy()

    # Parámetros globales
    p_iny = params.get("p_iny")
    p_inj_max = params.get("p_inj_max")
    mu = params.get("mu")
    d_pozo = params.get("d_pozo")
    rw = params.get("rw")

    # 1) BHP por zona
    df["bhp_zona"] = round(df["tvd"] * 0.433 + p_iny, 0)

    # 2) Delta de presión efectivo
    # 200 psi de fricción y pérdidas en VRF
    df["del_p"] = df["bhp_zona"] - df["py"] - 200

    # 3) BHP máximo por zona
    df["max_bhp_zona"] = round(df["tvd"] * 0.433 + p_inj_max, 0)

    # 4) Caudal sin daño (S=0)
    df["qscero"] = round(
        df.apply(
            lambda row: calcular_I_base(
                row["k_md"],
                row["h_ft"],
                mu,
                row["bhp_zona"],
                row["py"],
                d_pozo,
                rw,
                s=0
            ),
            axis=1
        ),
        0
    )

    # 5) Skin real
    df["s_real"] = round(
        df.apply(
            lambda row: estimar_skin(
                row["k_md"],
                row["h_ft"],
                mu,
                row["bhp_zona"],
                row["py"],
                d_pozo,
                rw,
                row["q_ilt"]
            ),
            axis=1
        ),
        2
    )


    df[["cumplimiento_obj", "flag_cumplimiento"]] = df.apply(
        cumplimiento_objetivo,
        axis=1,
        result_type="expand"
    )

    # 7) Diagnóstico corto
    df["diagnostico_corto"] = df.apply(diagnosticar_corto, axis=1)
    df["r35"] = df.apply(
        lambda row: calcular_r35(
            row["k_md"],
            row["porosidad"]
        ),
        axis=1
    )
    df["calidad_poro"] = df["r35"].apply(clasificar_calidad_poro)
    df["estado_presion"] = df["del_p"].apply(clasificar_estado_presion)
    
    return df