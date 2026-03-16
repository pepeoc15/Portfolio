import os
import geopandas as gpd
import pandas as pd

# === RUTAS (ajústalas a donde tengas los archivos) ===

BASE = "C:/Users/pepeo/Documents/UOC/UOC/visualizacion de datos/dgt-acc-viz/geo" 

files = {
    "ccaa_penin": os.path.join(BASE, "recintos_autonomicas_inspire_peninbal_etrs89.geojson"),
    "ccaa_can":   os.path.join(BASE, "recintos_autonomicas_inspire_canarias_regcan95.geojson"),

    "prov_penin": os.path.join(BASE, "recintos_provinciales_inspire_peninbal_etrs89.geojson"),
    "prov_can":   os.path.join(BASE, "recintos_provinciales_inspire_canarias_regcan95.geojson"),

    "mun_penin":  os.path.join(BASE, "recintos_municipales_inspire_peninbal_etrs89.geojson"),
    "mun_can":    os.path.join(BASE, "recintos_municipales_inspire_canarias_regcan95.geojson"),

    # opcional
    "zn_mel":     os.path.join(BASE, "Zona Neutral Marruecos-Melilla.geojson"),
    "zn_ceu":     os.path.join(BASE, "zonaneutral Marruecos-Ceuta.geojson"),
}

# === CRS objetivo ===
TARGET_EPSG = 4258   # ETRS89 (lat/lon)
PENIN_EPSG  = 4258   # tus archivos "etrs89" normalmente ya vienen en EPSG:4258
CAN_EPSG    = 4081   # REGCAN95

def read_with_fallback_crs(path: str, fallback_epsg: int) -> gpd.GeoDataFrame:
    """
    Lee GeoJSON con geopandas. Si no trae CRS, lo fuerza al fallback.
    """
    gdf = gpd.read_file(path)

    # Si el fichero no trae CRS (pasa a veces en GeoJSON), lo definimos.
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=fallback_epsg)

    return gdf

def to_target(gdf: gpd.GeoDataFrame, target_epsg: int = TARGET_EPSG) -> gpd.GeoDataFrame:
    """
    Reproyecta a CRS objetivo si hace falta.
    """
    if gdf.crs is None:
        raise ValueError("El GeoDataFrame no tiene CRS. Usa read_with_fallback_crs primero.")
    if gdf.crs.to_epsg() != target_epsg:
        gdf = gdf.to_crs(epsg=target_epsg)
    return gdf

def merge_two_levels(path_penin: str, path_can: str, out_path: str, name: str):
    print(f"\n--- Procesando: {name} ---")

    g_pen = read_with_fallback_crs(path_penin, PENIN_EPSG)
    g_can = read_with_fallback_crs(path_can, CAN_EPSG)

    g_pen = to_target(g_pen, TARGET_EPSG)
    g_can = to_target(g_can, TARGET_EPSG)

    # Unimos columnas (si no coinciden, se rellenan con NaN)
    merged = gpd.GeoDataFrame(
        pd.concat([g_pen, g_can], ignore_index=True),
        crs=f"EPSG:{TARGET_EPSG}"
    )

    # Limpieza opcional: eliminar geometrías vacías
    merged = merged[~merged.geometry.is_empty & merged.geometry.notnull()].copy()

    # Guardar
    merged.to_file(out_path, driver="GeoJSON")
    print(f"Guardado: {out_path} | features: {len(merged)} | CRS: {merged.crs}")

def merge_zonas_neutrales(out_path: str):
    paths = [files["zn_mel"], files["zn_ceu"]]
    gdfs = []
    for p in paths:
        if os.path.exists(p):
            g = gpd.read_file(p)
            # Si no trae CRS, asumimos ETRS89 por seguridad (ajusta si sabes otro)
            if g.crs is None:
                g = g.set_crs(epsg=TARGET_EPSG)
            g = to_target(g, TARGET_EPSG)
            gdfs.append(g)

    if not gdfs:
        print("\nNo se encontraron archivos de zona neutral; se omite.")
        return

    merged = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=f"EPSG:{TARGET_EPSG}")
    merged = merged[~merged.geometry.is_empty & merged.geometry.notnull()].copy()
    merged.to_file(out_path, driver="GeoJSON")
    print(f"\nGuardado zonas neutrales: {out_path} | features: {len(merged)} | CRS: {merged.crs}")

if __name__ == "__main__":
    # === 3 capas finales ===
    merge_two_levels(files["ccaa_penin"], files["ccaa_can"], "ccaa.geojson", "CCAA")
    merge_two_levels(files["prov_penin"], files["prov_can"], "provincias.geojson", "Provincias")
    merge_two_levels(files["mun_penin"],  files["mun_can"],  "municipios.geojson", "Municipios")

    # === opcional: zonas neutrales ===
    # merge_zonas_neutrales("zonas_neutrales.geojson")
