# scripts/build_dim_municipios.py
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


def extract_digits(s: str) -> str:
    return "".join(re.findall(r"\d+", str(s)))


def parse_natcode(natcode: str):
    """
    Intenta extraer:
      - ine5 = últimos 5 dígitos
      - prov2 = 2 dígitos anteriores a ine5
      - ccaa2 = 2 dígitos anteriores a prov2
    Si no hay suficientes dígitos, deja None.
    """
    digits = extract_digits(natcode)
    if len(digits) < 5:
        return None, None, None, None, None

    ine5 = digits[-5:]
    prov2 = digits[-7:-5] if len(digits) >= 7 else None
    ccaa2 = digits[-9:-7] if len(digits) >= 9 else None

    # mun3 son los últimos 3 del ine5
    mun3 = ine5[-3:]

    return digits, int(ine5), prov2, ccaa2, mun3


def main():
    base_dir = Path(__file__).resolve().parents[1]
    geo_path = base_dir / "geo" / "municipios.geojson"
    out_dir = base_dir / "data" / "dim"
    out_dir.mkdir(parents=True, exist_ok=True)

    geo = json.loads(geo_path.read_text(encoding="utf-8"))

    rows = []
    for f in geo.get("features", []):
        props = f.get("properties", {}) or {}
        natcode = str(props.get("NATCODE"))
        nameunit = props.get("NAMEUNIT")

        digits, ine5, prov2, ccaa2, mun3 = parse_natcode(natcode)

        rows.append(
            {
                "ine5": ine5,                     # int
                "natcode": natcode,               # original
                "natcode_digits": digits,         # solo dígitos (útil para debug)
                "ccaa2": ccaa2,                   # str (puede ser None)
                "prov2": prov2,                   # str (puede ser None)
                "mun3": mun3,                     # str
                "nameunit": nameunit,             # nombre municipio
            }
        )

    df = pd.DataFrame(rows)

    # Limpieza mínima
    df = df.dropna(subset=["ine5"]).drop_duplicates(subset=["ine5"])
    df = df.sort_values("ine5")

    out_path = out_dir / "municipios_dim.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")

    print(f"[OK] municipios_dim.csv generado: {out_path}")
    print(df.head(5))
    print(f"Filas: {len(df):,}")
    print("Nulos ccaa2/prov2 (por si el NATCODE no trae suficientes dígitos):",
          df["ccaa2"].isna().sum(), df["prov2"].isna().sum())


if __name__ == "__main__":
    main()
