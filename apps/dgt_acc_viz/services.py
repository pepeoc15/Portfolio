from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional
from .dicts import METRICS
import branca.colormap as cm


import pandas as pd
import folium



# INE / CCAA codes (2 dígitos)
# 01 Andalucía, 02 Aragón, 03 Asturias, 04 Illes Balears, 05 Canarias, 06 Cantabria,
# 07 Castilla y León, 08 Castilla-La Mancha, 09 Cataluña, 10 C. Valenciana,
# 11 Extremadura, 12 Galicia, 13 Madrid, 14 Murcia, 15 Navarra, 16 País Vasco,
# 17 La Rioja, 18 Ceuta, 19 Melilla
PROV_TO_CCAA_CODE: Dict[int, int] = {
    1: 16, 2: 8, 3: 10, 4: 1, 5: 7, 6: 11, 7: 4, 8: 9, 9: 7, 10: 11,
    11: 1, 12: 10, 13: 8, 14: 1, 15: 12, 16: 8, 17: 9, 18: 1, 19: 8, 20: 16,
    21: 1, 22: 2, 23: 1, 24: 7, 25: 9, 26: 17, 27: 12, 28: 13, 29: 1, 30: 14,
    31: 15, 32: 12, 33: 3, 34: 7, 35: 5, 36: 12, 37: 7, 38: 5, 39: 6, 40: 7,
    41: 1, 42: 7, 43: 9, 44: 2, 45: 8, 46: 10, 47: 7, 48: 16, 49: 7, 50: 2,
    51: 18, 52: 19,
}

CCAA_CODE_TO_NAME = {
    1: "Andalucía",
    2: "Aragón",
    3: "Principado de Asturias",
    4: "Illes Balears",
    5: "Canarias",
    6: "Cantabria",
    7: "Castilla-La Mancha",
    8: "Castilla y León",
    9: "Cataluña",
    10: "Comunitat Valenciana",
    11: "Extremadura",
    12: "Galicia",
    13: "Comunidad de Madrid",
    14: "Región de Murcia",
    15: "Navarra",
    16: "País Vasco",
    17: "La Rioja",
    18: "Ceuta",
    19: "Melilla",
}

def natcode_ccaa(ccaa_code: int) -> str:
    # 34 + ccaa(2) + 0000000  -> 11 dígitos
    return f"34{int(ccaa_code):02d}" + "0" * 7

def natcode_provincia(prov_code: int, ccaa_code: int) -> str:
    # 34 + ccaa(2) + prov(2) + 00000 -> 11 dígitos
    return f"34{int(ccaa_code):02d}{int(prov_code):02d}" + "0" * 5

def load_geojson(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def get_ccaa_choices() -> list[tuple[str, str]]:
    codes = sorted({int(v) for v in PROV_TO_CCAA_CODE.values() if v is not None})

    choices = []
    for c in codes:
        name = CCAA_CODE_TO_NAME.get(c, f"CCAA {c:02d}")
        choices.append((str(c), f"{name} ({c:02d})"))

    return choices


def get_provincia_choices(df: pd.DataFrame, ccaa_code: int | None = None) -> list[tuple[str, str]]:
    """
    Devuelve choices de provincia:
      - value: COD_PROVINCIA
      - label: "28 - Madrid"
    Si ccaa_code se pasa, filtra provincias que pertenecen a esa CCAA.
    """
    tmp = df[["COD_PROVINCIA", "COD_PROVINCIALITERAL"]].dropna().copy()
    tmp["COD_PROVINCIA"] = pd.to_numeric(tmp["COD_PROVINCIA"], errors="coerce")
    tmp["COD_PROVINCIALITERAL"] = tmp["COD_PROVINCIALITERAL"].astype(str).str.strip()
    tmp = tmp.dropna()

    ccaa_int: int | None = int(ccaa_code) if ccaa_code is not None else None

    if ccaa_int is not None:
        tmp["ccaa_code"] = tmp["COD_PROVINCIA"].map(PROV_TO_CCAA_CODE)
        tmp = tmp[tmp["ccaa_code"] == ccaa_int]

    tmp = tmp.drop_duplicates().sort_values(["COD_PROVINCIA"])

    return [
        (str(int(r.COD_PROVINCIA)), f"{int(r.COD_PROVINCIA):02d} - {r.COD_PROVINCIALITERAL}")
        for r in tmp.itertuples(index=False)
    ]

def prepare_geojson_join_by_natcode(geojson: dict, level: str) -> dict:
    """
    Inyecta properties.join_key:
      - provincia/ccaa: NATCODE completo (string)
      - municipio: INE5 (últimos 5 dígitos de NATCODE) como string de 5 dígitos
    """
    for f in geojson.get("features", []):
        props = f.setdefault("properties", {})
        nat = props.get("NATCODE")

        if level == "municipio":
            nat_s = "" if nat is None else str(nat)
            jk = None
            if len(nat_s) >= 5 and nat_s[-5:].isdigit():
                jk = nat_s[-5:]          # <-- "01059", "28079"
            props["join_key"] = jk
        else:
            props["join_key"] = str(nat) if nat is not None else None

    return geojson



def load_accidents_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, low_memory=False)

    # métricas a numérico (usamos SOLO las claves del dict)
    for col in METRICS.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # provincia / municipio (códigos INE)
    if "COD_PROVINCIA" in df.columns:
        df["COD_PROVINCIA"] = (
            pd.to_numeric(df["COD_PROVINCIA"], errors="coerce")
            .astype("Int64")
        )

    if "COD_MUNICIPIO" in df.columns:
        df["COD_MUNICIPIO"] = (
            pd.to_numeric(df["COD_MUNICIPIO"], errors="coerce")
            .astype("Int64")
        )

    return df



def get_anyos(df: pd.DataFrame) -> list[int]:
    if "ANYO" not in df.columns:
        return []
    s = pd.to_numeric(df["ANYO"], errors="coerce").dropna().astype(int)
    return sorted(s.unique().tolist())

def get_category_values(df: pd.DataFrame, col: str) -> list[str]:
    if col not in df.columns:
        return []
    vals = (
        df[col]
        .dropna()
        .astype(str)
        .str.strip()
        .replace({"": pd.NA})
        .dropna()
        .unique()
        .tolist()
    )
    return sorted(vals)

def filter_df(
    df: pd.DataFrame,
    acumulado: bool,
    anyo: int | None,
    tipo_via: str | None,
    tipo_accidente: str | None,
    ccaa_code: int | None = None,
    cod_provincia: int | None = None,
) -> pd.DataFrame:
    out = df

    if not acumulado and anyo is not None and "ANYO" in out.columns:
        out = out[pd.to_numeric(out["ANYO"], errors="coerce").astype("Int64") == int(anyo)]

    if tipo_via and tipo_via != "__all__" and "TIPO_VIA" in out.columns:
        sel = pd.to_numeric(tipo_via, errors="coerce")
        col = pd.to_numeric(out["TIPO_VIA"], errors="coerce").astype("Int64")
        if pd.notna(sel):
            out = out[col == int(sel)]

    # ---------- FIX TIPO_ACCIDENTE ----------
    if tipo_accidente and tipo_accidente != "__all__" and "TIPO_ACCIDENTE" in out.columns:
        sel = pd.to_numeric(tipo_accidente, errors="coerce")
        col = pd.to_numeric(out["TIPO_ACCIDENTE"], errors="coerce").astype("Int64")
        if pd.notna(sel):
            out = out[col == int(sel)]

    # NUEVO: provincia
    if cod_provincia is not None and "COD_PROVINCIA" in out.columns:
        out = out[pd.to_numeric(out["COD_PROVINCIA"], errors="coerce").astype("Int64") == int(cod_provincia)]

    # NUEVO: ccaa (vía provincia->ccaa)
    if ccaa_code is not None and "COD_PROVINCIA" in out.columns:
        prov = pd.to_numeric(out["COD_PROVINCIA"], errors="coerce").astype("Int64")
        out = out[prov.map(PROV_TO_CCAA_CODE).astype("Int64") == int(ccaa_code)]

    return out



def aggregate_for_level(df: pd.DataFrame, level: str, metric: str) -> pd.DataFrame:
    """
    Devuelve columnas: join_key (NATCODE) + value (suma)
    """
    if level == "provincia":
        tmp = df.copy()
        tmp["prov_code"] = pd.to_numeric(tmp["COD_PROVINCIA"], errors="coerce").astype("Int64")
        tmp["ccaa_code"] = tmp["prov_code"].map(PROV_TO_CCAA_CODE)

        tmp = tmp.dropna(subset=["prov_code", "ccaa_code"])

        # NATCODE provincia
        tmp["join_key"] = (
            "34"
            + tmp["ccaa_code"].astype(int).astype(str).str.zfill(2)
            + tmp["prov_code"].astype(int).astype(str).str.zfill(2)
            + "00000"
        )

        out = (
            tmp.groupby("join_key")[metric]
            .sum()
            .reset_index()
            .rename(columns={metric: "value"})
        )
        return out


    elif level == "ccaa":
        tmp = df.copy()
        tmp["prov_code"] = pd.to_numeric(tmp["COD_PROVINCIA"], errors="coerce").astype("Int64")
        tmp["ccaa_code"] = tmp["prov_code"].map(PROV_TO_CCAA_CODE)

        tmp = tmp.dropna(subset=["ccaa_code"])

        tmp["join_key"] = (
            "34"
            + tmp["ccaa_code"].astype(int).astype(str).str.zfill(2)
            + "0000000"
        )

        out = (
            tmp.groupby("join_key")[metric]
            .sum()
            .reset_index()
            .rename(columns={metric: "value"})
        )
        return out

    
    elif level == "municipio":
        tmp = df.copy()

        prov = pd.to_numeric(tmp["COD_PROVINCIA"], errors="coerce").astype("Int64")
        mun  = pd.to_numeric(tmp["COD_MUNICIPIO"], errors="coerce").astype("Int64")

        ine5 = mun.where(mun >= 10000, prov * 1000 + (mun % 1000))

        tmp["join_key"] = (
            ine5.dropna()
                .astype(int)
                .astype(str)
                .str.zfill(5)       # <-- "01059"
        )

        out = (
            tmp.dropna(subset=["join_key"])
            .groupby("join_key")[metric]
            .sum()
            .reset_index()
            .rename(columns={metric: "value"})
        )
        return out



    raise ValueError("level debe ser 'provincia', 'ccaa' o 'municipio'.")


def build_choropleth(geojson: dict, data: pd.DataFrame, legend: str, level: str) -> folium.Map:
    zoom = 6 if level in ("provincia", "ccaa") else 7
    m = folium.Map(location=[40.2, -3.7], zoom_start=zoom, tiles="cartodbpositron")

    # dict join_key(str) -> value
    data_map = dict(zip(data["join_key"].astype(str), data["value"]))

    values = list(data_map.values())
    vmin = min(values) if values else 0
    vmax = max(values) if values else 1

    colormap = cm.LinearColormap(["#f7fbff", "#08306b"], vmin=vmin, vmax=vmax)
    colormap.caption = legend
    colormap.add_to(m)

    # ✅ Inyecta "value" EN TODAS las features ANTES de crear la capa GeoJson
    for f in geojson.get("features", []):
        props = f.setdefault("properties", {})
        jk = str(props.get("join_key"))
        # value siempre existe (aunque sea None)
        val = data_map.get(jk, 0)
        props["value"] = float(val)


    def style_fn(feature):
        props = feature.get("properties", {})
        val = props.get("value")
        if val is None:
            return {"fillColor": "#ffffff", "color": "#666", "weight": 0.5, "fillOpacity": 0.15}
        return {"fillColor": colormap(val), "color": "#666", "weight": 0.5, "fillOpacity": 0.75}

    def highlight_fn(_):
        return {"weight": 2, "color": "#111"}

    # ✅ Un único tooltip (sin "value" inexistente)
    tooltip = folium.GeoJsonTooltip(
        fields=["NAMEUNIT", "join_key", "value"],
        aliases=["Zona", "Código", "Valor"],
        localize=True,
        sticky=True,
        labels=True,
    )

    folium.GeoJson(
        geojson,
        name="Zonas",
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=tooltip,
    ).add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)
    return m

