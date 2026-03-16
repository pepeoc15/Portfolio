from django import forms

def _add_class(widget, css: str):
    current = widget.attrs.get("class", "")
    classes = set(current.split()) if current else set()
    classes.add(css)
    widget.attrs["class"] = " ".join(sorted(classes))

class MapForm(forms.Form):
    # ... tus fields aquí ...
    LEVEL_CHOICES = [
    ("provincia", "Provincia"),
    ("ccaa", "Comunidad Autónoma"),
    ("municipio", "Municipio"),
    ]

    level = forms.ChoiceField(choices=LEVEL_CHOICES, initial="provincia")
    ccaa = forms.ChoiceField(choices=[], required=False)
    provincia = forms.ChoiceField(choices=[], required=False)

    # nuevo
    acumulado = forms.BooleanField(required=False, initial=False)
    anyo = forms.ChoiceField(choices=[], required=False)

    metric = forms.ChoiceField(choices=[], required=True)

    # nuevos filtros (opcionales)
    tipo_via = forms.ChoiceField(choices=[], required=False)
    tipo_accidente = forms.ChoiceField(choices=[], required=False)

    def __init__(
        self,
        *args,
        metric_choices=None,
        anyo_choices=None,
        tipo_via_choices=None,
        tipo_accidente_choices=None,
        ccaa_choices=None,
        provincia_choices=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        # Asigna choices (sin reventar si falta algún field)
        if "metric" in self.fields:
            self.fields["metric"].choices = metric_choices or []
        if "anyo" in self.fields:
            self.fields["anyo"].choices = anyo_choices or []
        if "tipo_via" in self.fields:
            self.fields["tipo_via"].choices = tipo_via_choices or []
        if "tipo_accidente" in self.fields:
            self.fields["tipo_accidente"].choices = tipo_accidente_choices or []
        if "ccaa" in self.fields:
            self.fields["ccaa"].choices = ccaa_choices or []
        if "provincia" in self.fields:
            self.fields["provincia"].choices = provincia_choices or []

        # Estilos bootstrap
        for name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                _add_class(field.widget, "form-check-input")
            elif isinstance(field, forms.ChoiceField):
                _add_class(field.widget, "form-select")
            else:
                _add_class(field.widget, "form-control")
