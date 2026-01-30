from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from .dicts import make_choices, make_choices_from_df,make_metric_choices, METRICS


from .forms import MapForm
from .services import (
    PROV_TO_CCAA_CODE,
    load_geojson,
    prepare_geojson_join_by_natcode,   # <-- AÑADIR
    load_accidents_csv,
    get_anyos,
    get_ccaa_choices,
    get_provincia_choices,
    filter_df,
    aggregate_for_level,
    build_choropleth,
)

BASE_DIR = Path(settings.BASE_DIR)

def index(request):
    level = request.GET.get("level", "provincia")  # provincia | ccaa

    acumulado = request.GET.get("acumulado") in ("on", "1", "true", "True")

    csv_path = BASE_DIR / "data" / "accidentes_dgt.csv"
    df = load_accidents_csv(csv_path)
    print("tipo via",df["TIPO_VIA"].dropna().unique()[:10])
    print("tipo accidente",df["TIPO_ACCIDENTE"].dropna().unique()[:10])


    anyos = get_anyos(df)
    anyo_choices = [("__all__", "—")] + [(str(a), str(a)) for a in anyos]

    default_anyo = str(anyos[-1]) if anyos else "__all__"
    anyo = request.GET.get("anyo", default_anyo)

    tipo_via_choices = make_choices_from_df(
        df,
        code_col="TIPO_VIA",
        label_col="TIPO_VIALITERAL",
        all_label="Todas"
    )

    tipo_acc_choices = make_choices_from_df(
        df,
        code_col="TIPO_ACCIDENTE",
        label_col="TIPO_ACCIDENTELITERAL",
        all_label="Todos"
    )


    tipo_via = request.GET.get("tipo_via", "__all__")
    tipo_accidente = request.GET.get("tipo_accidente", "__all__")

    ccaa = request.GET.get("ccaa", "__all__")
    provincia = request.GET.get("provincia", "__all__")

    ccaa_choices = [("__all__", "Todas")] + get_ccaa_choices()

    ccaa_int = None if ccaa in (None, "", "__all__") else int(ccaa)
    provincia_choices = [("__all__", "Todas")] + get_provincia_choices(df, ccaa_code=ccaa_int)

    metric_choices = [
    (k, v) for k, v in make_metric_choices()
    if k in df.columns
    ]

    metric = request.GET.get(
        "metric",
        metric_choices[0][0] if metric_choices else None
    )

    df_f = filter_df(
        df,
        acumulado=acumulado,
        anyo=None if anyo in (None, "", "__all__") else int(anyo),
        tipo_via=None if tipo_via in (None, "", "__all__") else tipo_via,
        tipo_accidente=None if tipo_accidente in (None, "", "__all__") else tipo_accidente,
        ccaa_code=None if ccaa in (None, "", "__all__") else int(ccaa),
        cod_provincia=None if provincia in (None, "", "__all__") else int(provincia),
    )

    # geojson
    if level == "provincia":
        geo_path = BASE_DIR / "geo" / "provincias_espana.geojson"
    elif level == "ccaa":
        geo_path = BASE_DIR / "geo" / "ccaa_espana.geojson"
    else:
        geo_path = BASE_DIR / "geo" / "municipios_espana.geojson"
    geojson = load_geojson(geo_path)
    geojson = prepare_geojson_join_by_natcode(geojson,level=level)  # <-- CLAVE (inyecta join_key)

    name_map = {}
    for f in geojson.get("features", []):
        props = f.get("properties", {})
        k = str(props.get("join_key") or props.get("NATCODE") or "")
        name = props.get("NAMEUNIT") or props.get("name")
        if k and name:
            name_map[k] = name

    validation_error = None

    if level == "municipio" and ccaa in ("__all__", "", None) and provincia in ("__all__", "", None):
        validation_error = "Selecciona una CCAA o una provincia para ver el nivel municipio."

    top10 = []
    # mapa
    map_html = ""
    if metric and not validation_error:
        agg = aggregate_for_level(df_f, level, metric)
        agg["label"] = agg["join_key"].astype(str).map(name_map).fillna(agg["join_key"].astype(str))

        if level == "municipio":
            # Filtrar geojson por territorio (provincia o ccaa), NO por municipios con dato
            if provincia not in ("__all__", "", None):
                prov2 = f"{int(provincia):02d}"
                geojson["features"] = [
                    f for f in geojson.get("features", [])
                    if str(f.get("properties", {}).get("join_key", "")).startswith(prov2)
                ]
            elif ccaa not in ("__all__", "", None):
                allowed_provs = {p for p, c in PROV_TO_CCAA_CODE.items() if int(c) == int(ccaa)}
                allowed_prefix = {f"{int(p):02d}" for p in allowed_provs}
                geojson["features"] = [
                    f for f in geojson.get("features", [])
                    if str(f.get("properties", {}).get("join_key", "")).zfill(5)[:2] in allowed_prefix
                ]

        metric_label = METRICS.get(metric, metric)
        legend = f"{metric_label} ({'acumulado' if acumulado else 'año ' + str(anyo)})"
        m = build_choropleth(geojson, agg, legend=legend, level=level)
        map_html = m._repr_html_()

        top10 = (
        agg.sort_values("value", ascending=False)
        .head(10)[["label", "value"]]
        .to_dict(orient="records")
        )

    form = MapForm(
        request.GET or None,
        metric_choices=metric_choices,
        anyo_choices=anyo_choices,
        tipo_via_choices=tipo_via_choices,
        tipo_accidente_choices=tipo_acc_choices,
        ccaa_choices=ccaa_choices,
        provincia_choices=provincia_choices,
    )
    
        

    return render(request, "viz/index.html", {
        "form": form,
        "map_html": map_html,
        "validation_error": validation_error,
        "top10": top10,
        "metric": metric,
        "level": level,
    })
