from __future__ import annotations

import pandas as pd
from pathlib import Path

CSV_PATH = Path("data/accidentes_dgt.csv")

PAIRS = [
    ("TIPO_VIA", "TIPO_VIALITERAL"),
    ("TIPO_ACCIDENTE", "TIPO_ACCIDENTELITERAL"),
    ("ZONA", "ZONALITERAL"),
    ("ZONA_AGRUPADA", "ZONA_AGRUPADALITERAL"),
    # más adelante:
    # ("NUDO", "NUDOLITERAL"),
    # ("NUDO_INFO", "NUDO_INFOLITERAL"),
]

def build_map(df: pd.DataFrame, code_col: str, lit_col: str) -> dict[int, str]:
    tmp = df[[code_col, lit_col]].dropna().copy()
    tmp[lit_col] = tmp[lit_col].astype(str).str.strip()
    tmp[code_col] = pd.to_numeric(tmp[code_col], errors="coerce").astype("Int64")
    tmp = tmp.dropna(subset=[code_col]).drop_duplicates(subset=[code_col], keep="first")

    m = {int(k): v for k, v in zip(tmp[code_col], tmp[lit_col])}
    # orden por clave para que sea estable
    return dict(sorted(m.items(), key=lambda kv: kv[0]))

def pretty_dict(name: str, mapping: dict[int, str]) -> str:
    lines = [f"{name}: dict[int, str] = {{"]
    for k, v in mapping.items():
        v_escaped = v.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'    {k}: "{v_escaped}",')
    lines.append("}\n")
    return "\n".join(lines)

def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"No encuentro el CSV en {CSV_PATH.resolve()}")

    df = pd.read_csv(CSV_PATH, low_memory=False)
    text = []

    for code_col, lit_col in PAIRS:
        if code_col not in df.columns or lit_col not in df.columns:
            print(f"# Saltando {code_col} (faltan columnas)")
            continue
        mapping = build_map(df, code_col, lit_col)
        print(pretty_dict(code_col, mapping))
        text.append(pretty_dict(code_col, mapping))
        

    Path("dicts_out.txt").write_text("".join(text), encoding="utf-8")
    print("OK: dicts_out.txt generado en UTF-8")


if __name__ == "__main__":
    main()
