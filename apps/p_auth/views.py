from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404
from django.urls import reverse


class AppLoginView(LoginView):
    template_name = "p_auth/login.html"

    def dispatch(self, request, *args, **kwargs):
        self.app_key = kwargs.get("app_key")
        self.app_config = None

        if self.app_key:
            self.app_config = settings.APP_AUTH_CONFIG.get(self.app_key)
            if not self.app_config:
                raise Http404("Aplicación no registrada")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.app_config:
            context["app_label"] = self.app_config.get("label")
            register_url_name = self.app_config.get("register_url_name")
            if register_url_name:
                context["register_url"] = reverse(register_url_name)

        return context

    def get_success_url(self):
        if self.app_config and self.app_config.get("join_url_name"):
            return reverse(self.app_config["join_url_name"])
        return super().get_success_url()


class AppLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        self.app_key = kwargs.get("app_key")
        self.app_config = None

        if self.app_key:
            self.app_config = settings.APP_AUTH_CONFIG.get(self.app_key)
            if not self.app_config:
                raise Http404("Aplicación no registrada")

        return super().dispatch(request, *args, **kwargs)

    def get_default_redirect_url(self):
        if self.app_config and self.app_config.get("logout_redirect_url_name"):
            return reverse(self.app_config["logout_redirect_url_name"])
        return settings.LOGOUT_REDIRECT_URL