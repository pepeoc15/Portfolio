from __future__ import annotations

from pathlib import Path
import pytest
import pandas as pd

from viz.services import (
    load_geojson,
    prepare_geojson_join_by_natcode,
    load_accidents_csv,
    get_anyos,
    filter_df,
    aggregate_for_level,
)
from viz.dicts import METRICS, DICT_REGISTRY


BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "accidentes_dgt.csv"
GEO_PROV = BASE_DIR / "geo" / "provincias.geojson"
GEO_CCAA = BASE_DIR / "geo" / "ccaa.geojson"


@pytest.fixture(scope="session")
def df() -> pd.DataFrame:
    return load_accidents_csv(CSV_PATH)


@pytest.fixture(scope="session")
def geo_prov() -> dict:
    return prepare_geojson_join_by_natcode(load_geojson(GEO_PROV))


@pytest.fixture(scope="session")
def geo_ccaa() -> dict:
    return prepare_geojson_join_by_natcode(load_geojson(GEO_CCAA))


def _codes(dict_name: str) -> list[str]:
    # choices como string para simular GET params
    mapping = DICT_REGISTRY.get(dict_name, {})
    return ["__all__"] + [str(k) for k in sorted(mapping.keys())]


def _validate_agg(agg: pd.DataFrame):
    assert isinstance(agg, pd.DataFrame)
    assert "join_key" in agg.columns
    assert "value" in agg.columns
    assert agg["join_key"].dtype == object
    # value debe ser numérico
    assert pd.api.types.is_numeric_dtype(agg["value"])
    # no negativos (en estas métricas)
    assert (agg["value"] >= 0).all()


def _match_ratio(geojson: dict, agg: pd.DataFrame) -> float:
    keys = set(agg["join_key"].dropna().astype(str))
    feats = geojson.get("features", [])
    if not feats:
        return 0.0
    hits = 0
    for f in feats:
        jk = f.get("properties", {}).get("join_key")
        if jk is not None and str(jk) in keys:
            hits += 1
    return hits / len(feats)

def _geo_join_keys(geojson: dict) -> set[str]:
    return {
        str(f.get("properties", {}).get("join_key"))
        for f in geojson.get("features", [])
        if f.get("properties", {}).get("join_key") is not None
    }

def _unknown_keys(geojson: dict, agg: pd.DataFrame) -> list[str]:
    geo_keys = _geo_join_keys(geojson)
    agg_keys = set(agg["join_key"].dropna().astype(str))
    return sorted(agg_keys - geo_keys)


@pytest.mark.parametrize("level", ["provincia", "ccaa"])
@pytest.mark.parametrize("acumulado", [False, True])
def test_combinaciones_exhaustivo(df, geo_prov, geo_ccaa, level, acumulado):
    geojson = geo_prov if level == "provincia" else geo_ccaa

    metrics = [m for m in METRICS.keys() if m in df.columns]
    assert metrics, "No se detectaron métricas en el CSV"

    anyos = get_anyos(df)
    assert anyos, "No se detectaron años en el CSV"

    tipo_via_codes = _codes("TIPO_VIA")
    tipo_acc_codes = _codes("TIPO_ACCIDENTE")

    # si acumulado=True, no iteramos por año (se usa el total)
    years_to_test = [None] if acumulado else anyos

    # Recorremos combinaciones
    for metric in metrics:
        for anyo in years_to_test:
            for tipo_via in tipo_via_codes:
                for tipo_acc in tipo_acc_codes:
                    df_f = filter_df(
                        df,
                        acumulado=acumulado,
                        anyo=anyo,
                        tipo_via=None if tipo_via == "__all__" else tipo_via,
                        tipo_accidente=None if tipo_acc == "__all__" else tipo_acc,
                    )

                    # No exigimos que haya filas para todas las combinaciones (puede no existir)
                    if df_f.empty:
                        continue

                    agg = aggregate_for_level(df_f, level, metric)
                    _validate_agg(agg)

                    # Validación suave: que al menos un % de features matchee
                    unknown = _unknown_keys(geojson, agg)

                    # Si te faltan Ceuta/Melilla en el geojson peninsular, permite esas claves:
                    allowed = set()  # o {"34180000000", "34190000000"} si aplica a tu caso
                    unknown = [k for k in unknown if k not in allowed]

                    assert not unknown, (
                        f"Hay join_key que no existen en el geojson: {unknown[:10]} "
                        f"(total {len(unknown)}) "
                        f"level={level} metric={metric} anyo={anyo} tipo_via={tipo_via} tipo_acc={tipo_acc}"
                    )

