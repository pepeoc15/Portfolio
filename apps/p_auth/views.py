from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.contrib.auth.views import LoginView


class AppLoginView(LoginView):
    template_name = "p_auth/login.html"

    def dispatch(self, request, *args, **kwargs):
        self.app_key = kwargs.get("app_key")
        self.app_config = None

        if self.app_key:
            self.app_config = getattr(settings, "APP_AUTH_CONFIG", {}).get(self.app_key)
            if not self.app_config:
                raise Http404("Aplicación no registrada para autenticación")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.app_config:
            context["app_key"] = self.app_key
            context["app_label"] = self.app_config["label"]
            context["register_url"] = reverse(self.app_config["register_url_name"])
            context["join_url"] = reverse(self.app_config["join_url_name"])

        return context

    def get_success_url(self):
        if self.app_config:
            return reverse(self.app_config["join_url_name"])
        return super().get_success_url()