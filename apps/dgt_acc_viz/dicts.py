from __future__ import annotations
from typing import Dict, Tuple
import pandas as pd

# =========================================================
# Diccionarios CODE -> LITERAL (pegados “a mano”)
# Se generan ejecutando: tests/calcular_dict.py
# =========================================================

METRICS: dict[str, str] = {
    "TOTAL_MU24H": "Total de fallecidos a las 24 h",
    "TOTAL_HG24H": "Total de heridos graves a las 24 h",
    "TOTAL_HL24H": "Total de heridos leves a las 24 h",
    "TOTAL_MU30DF": "Total de fallecidos a 30 días",
    "TOTAL_HG30DF": "Total de heridos graves a 30 días",
    "TOTAL_HL30DF": "Total de heridos leves a 30 días",
}

def make_metric_choices() -> list[tuple[str, str]]:
    """
    Choices Django para métricas:
    [("TOTAL_MU24H", "Total de fallecidos a las 24 h"), ...]
    """
    return [(k, v) for k, v in METRICS.items()]


TIPO_VIA: dict[int, str] = {
    1: "Autopista de peaje",
    2: "Autopista libre",
    3: "Autovía",
    4: "Vía para automóviles",
    5: "Carretera Convencional de doble calzada",
    6: "Carretera Convencional de calzada única",
    7: "Vía de servicio",
    8: "Ramal de enlace",
    9: "Calle",
    10: "Camino vecinal",
    11: "Recinto delimitado",
    12: "Vía ciclista",
    13: "Senda ciclable",
    14: "Otro",
}

TIPO_ACCIDENTE: dict[int, str] = {
    1: "Frontal",
    2: "Fronto-lateral",
    3: "Lateral",
    4: "Por alcance",
    5: "Múltiple o en caravana",
    6: "Colisión contra obstáculo o elemento de la vía",
    7: "Atropello a personas",
    8: "Atropello a animales",
    9: "Vuelco",
    10: "Caída",
    11: "Sólo salida de la vía",
    12: "Salida de la vía por la izquierda con colisión",
    13: "Salida de la vía por la izquierda con despeñamiento",
    14: "Salida de la vía por la izquierda con vuelco",
    15: "Salida de la vía por la izquierda, otro tipo",
    16: "Salida de la vía por la derecha con colisión",
    17: "Salida de la vía por la derecha con despeñamiento",
    18: "Salida de la vía por la derecha con vuelco",
    19: "Salida de la vía por la derecha otro tipo",
    20: "Otro tipo de accidente",
}

ZONA: dict[int, str] = {
    1: "Carretera",
    2: "Travesía",
    3: "Calle",
    4: "Autopista o autovía urbana",
}

ZONA_AGRUPADA: dict[int, str] = {
    1: "VÍAS INTERURBANAS",
    2: "VÍAS URBANAS",
}


NUDO: Dict[int, str] = {
    # más adelante
}

NUDO_INFO: Dict[int, str] = {
    # más adelante
}


# Registro único de todos los diccionarios
DICT_REGISTRY: Dict[str, Dict[int, str]] = {
    "TIPO_VIA": TIPO_VIA,
    "TIPO_ACCIDENTE": TIPO_ACCIDENTE,
    "ZONA": ZONA,
    "ZONA_AGRUPADA": ZONA_AGRUPADA,
    "NUDO": NUDO,
    "NUDO_INFO": NUDO_INFO,
}

def make_choices(dict_name: str, all_label: str) -> list[Tuple[str, str]]:
    """
    Devuelve choices Django: [("__all__", "..."), ("1", "Autovía"), ...]
    Ordenado por literal.
    """
    mapping = DICT_REGISTRY.get(dict_name, {})
    items = sorted(mapping.items(), key=lambda kv: kv[1])
    return [("__all__", all_label)] + [(str(k), v) for k, v in items]

def make_choices_from_df(
    df: pd.DataFrame,
    code_col: str,
    label_col: str,
    all_label: str
) -> list[tuple[str, str]]:
    """
    Crea choices Django SOLO con los códigos presentes en el dataset.
    value = código
    label = literal
    """
    tmp = df[[code_col, label_col]].copy()

    tmp[code_col] = pd.to_numeric(tmp[code_col], errors="coerce").astype("Int64")
    tmp[label_col] = tmp[label_col].astype(str).str.strip()

    tmp = tmp.dropna(subset=[code_col])
    tmp = tmp.drop_duplicates(subset=[code_col])

    items = sorted(
        ((str(int(k)), v) for k, v in zip(tmp[code_col], tmp[label_col])),
        key=lambda kv: kv[1]
    )

    return [("__all__", all_label)] + items
