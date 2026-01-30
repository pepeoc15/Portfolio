import json
import pandas as pd
from pathlib import Path
from services import aggregate_for_level, load_accidents_csv

df = load_accidents_csv(Path("data/accidentes_dgt.csv"))

print("porcentaje de nulos en el campo carretera:", df["CARRETERA"].isna().mean())

# valuecounts de el campo carretera
vc = df["CARRETERA"].value_counts(dropna=False)
print("Value counts de CARRETERA:")
print(vc)
# porcentaje sobre el total
print("Porcentajes:")
print(vc / len(df))