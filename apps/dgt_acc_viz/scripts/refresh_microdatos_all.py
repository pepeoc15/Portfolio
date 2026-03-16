from __future__ import annotations

import re
from pathlib import Path
import requests
import pandas as pd

from services import PROV_TO_CCAA_CODE


SPARQL_ENDPOINT = "https://datos.gob.es/virtuoso/sparql"

QUERY = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct:  <http://purl.org/dc/terms/>

SELECT ?title ?accessURL
WHERE {
  ?dataset a dcat:Dataset ;
           dct:title ?title ;
           dcat:distribution ?distribution .

  ?distribution dcat:accessURL ?accessURL .

  FILTER (lang(?title) = "es")
  FILTER (CONTAINS(LCASE(STR(?title)), "microdatos"))
  FILTER (CONTAINS(LCASE(STR(?title)), "accidentes"))
  FILTER (CONTAINS(LCASE(STR(?title)), "víctimas"))

  FILTER (
    CONTAINS(LCASE(STR(?accessURL)), ".xlsx") ||
    CONTAINS(LCASE(STR(?accessURL)), ".xls")
  )
}
ORDER BY ?title
"""


def extract_year(text: str) -> int | None:
    m = re.search(r"(20\d{2})", text)
    return int(m.group(1)) if m else None


def discover_sources() -> pd.DataFrame:
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "dgt-acc-viz/1.0 (python requests)"
    }
    params = {"query": QUERY, "format": "application/sparql-results+json"}

    r = requests.get(SPARQL_ENDPOINT, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    bindings = r.json()["results"]["bindings"]

    rows = []
    for item in bindings:
        title = item["title"]["value"]
        url = item["accessURL"]["value"]
        year = extract_year(title) or extract_year(url)
        rows.append({"year": year, "title": title, "xlsx_url": url})

    df = pd.DataFrame(rows).drop_duplicates(subset=["xlsx_url"])
    df = df.dropna(subset=["year"]).sort_values("year").reset_index(drop=True)
    return df


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return

    with requests.get(url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def to_int_safe(x):
    if pd.isna(x):
        return None
    try:
        return int(float(x))
    except Exception:
        return None


def compute_ine5_and_join_mun(cod_provincia, cod_municipio):
    prov = to_int_safe(cod_provincia)
    mun = to_int_safe(cod_municipio)
    if prov is None or mun is None:
        return None

    # si ya viene INE5
    if mun >= 10000:
        ine5 = mun
        mun3 = ine5 % 1000
        join_mun = ine5 if mun3 != 0 else None
        return join_mun

    mun3 = mun % 1000
    ine5 = prov * 1000 + mun3
    join_mun = ine5 if mun3 != 0 else None
    return join_mun


def build_natcode(prov, mun) -> str | None:
    if prov is None or pd.isna(prov):
        return None

    country = "34"  # España
    prov_i = int(prov)

    ccaa = str(PROV_TO_CCAA_CODE.get(prov_i))
    prov_str = f"{prov_i:02d}"

    # Municipio vacío / NaN / 0
    if mun is None or pd.isna(mun) or int(mun) == 0:
        return f"{country}{ccaa}{prov_str}{prov_str}000"

    mun_i = int(mun)
    mun_str = f"{mun_i:03d}"

    return f"{country}{ccaa}{prov_str}{prov_str}{mun_str}"



def process_one_year(year: int, xlsx_url: str, dim: pd.DataFrame, raw_dir: Path) -> pd.DataFrame:
    raw_path = raw_dir / f"microdatos_{year}.xlsx"
    download_file(xlsx_url, raw_path)

    df = pd.read_excel(raw_path)
    df.columns = [str(c).strip() for c in df.columns]

    required = ["COD_PROVINCIA", "COD_MUNICIPIO"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"[{year}] Faltan columnas en el Excel: {missing}")

    df["ANYO"] = int(year)
    df["natcode"] = [
        build_natcode(prov, mun)
        for prov, mun in zip(df["COD_PROVINCIA"], df["COD_MUNICIPIO"])
    ]

    


    meta_dir = Path(__file__).resolve().parents[1] / "data" / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)




    # Métricas a int si están
    metric_cols = [
        "TOTAL_MU24H", "TOTAL_HG24H", "TOTAL_HL24H",
        "TOTAL_MU30DF", "TOTAL_HG30DF", "TOTAL_HL30DF"
    ]
    for c in metric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    return df


def main():
    base_dir = Path(__file__).resolve().parents[1]

    dim_path = base_dir / "data" / "dim" / "municipios_dim.csv"
    if not dim_path.exists():
        raise RuntimeError("No existe data/dim/municipios_dim.csv. Ejecuta build_dim_municipios.py")

    dim = pd.read_csv(
        dim_path,
        dtype={"ccaa2": "string", "prov2": "string", "mun3": "string"}
    )

    sources = discover_sources()

    # guarda trazabilidad
    meta_dir = base_dir / "data" / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    sources.to_csv(meta_dir / "microdatos_sources.csv", index=False, encoding="utf-8")

    raw_dir = base_dir / "data" / "raw"
    out_dir = base_dir / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    print("=== Descargando y procesando años ===")
    for _, row in sources.iterrows():
        year = int(row["year"])
        url = row["xlsx_url"]
        print(f"-> {year}  {url}")
        try:
            df_year = process_one_year(year, url, dim, raw_dir)
            
            unmatched = df_year["natcode"].isna().sum() if "natcode" in df_year.columns else None
            print(f"   filas: {len(df_year):,} | sin natcode (dim): {unmatched:,}" if unmatched is not None else f"   filas: {len(df_year):,}")
            frames.append(df_year)
        except Exception as e:
            print(f"[WARN] Año {year} falló: {e}")
            raise e

    if not frames:
        raise RuntimeError("No se ha podido procesar ningún año.")

    df_all = pd.concat(frames, ignore_index=True)

    # export final
    out_path = out_dir / "accidentes_all.csv"
    df_all.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\n[OK] Generado: {out_path} | filas totales: {len(df_all):,}")

    # opcional: parquet (mucho más rápido)
    try:
        parquet_path = out_dir / "accidentes_all.parquet"
        df_all.to_parquet(parquet_path, index=False)
        print(f"[OK] Generado: {parquet_path}")
    except Exception:
        print("[INFO] Parquet no generado (instala pyarrow si lo quieres).")


if __name__ == "__main__":
    main()
