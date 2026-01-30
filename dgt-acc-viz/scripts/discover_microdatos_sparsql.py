# scripts/discover_microdatos_sparql.py
from __future__ import annotations

import re
import requests
import pandas as pd

SPARQL_ENDPOINT = "https://datos.gob.es/virtuoso/sparql"  # <-- ESTE

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

def main():
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

    df = pd.DataFrame(rows).drop_duplicates(subset=["xlsx_url"]).sort_values("year")
    print(df[["year", "xlsx_url"]].to_string(index=False))
    return df

if __name__ == "__main__":
    main()
