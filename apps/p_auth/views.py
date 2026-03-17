from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import RegisterForm


def onboard_user_for_app(user, app_key):
    if app_key == "moc_beauty":
        from apps.moc_beauty.models import MBRole, MBMembership

        role = MBRole.objects.get(code="CLIENTE")
        MBMembership.objects.get_or_create(
            user=user,
            role=role,
            defaults={"active": True},
        )
        return

    raise ValueError(f"No onboarding handler for app_key={app_key}")


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
            context["app_label"] = self.app_config.get("label")
            if self.app_config.get("register_enabled"):
                context["register_url"] = reverse("p_auth:app_register", args=[self.app_key])

        return context

    def get_success_url(self):
        if self.app_config and self.app_config.get("join_url_name"):
            return reverse(self.app_config["join_url_name"])
        return super().get_success_url()


class AppLogoutView(LogoutView):
    http_method_names = ["get", "post", "options"]

    def dispatch(self, request, *args, **kwargs):
        self.app_key = kwargs.get("app_key")
        self.app_config = None

        if self.app_key:
            self.app_config = getattr(settings, "APP_AUTH_CONFIG", {}).get(self.app_key)
            if not self.app_config:
                raise Http404("Aplicación no registrada para autenticación")

        return super().dispatch(request, *args, **kwargs)

    def get_default_redirect_url(self):
        if self.app_config and self.app_config.get("logout_redirect_url_name"):
            return reverse(self.app_config["logout_redirect_url_name"])
        return settings.LOGOUT_REDIRECT_URL


def register_view(request, app_key=None):
    app_config = None

    if app_key:
        app_config = getattr(settings, "APP_AUTH_CONFIG", {}).get(app_key)
        if not app_config:
            raise Http404("Aplicación no registrada para autenticación")

    if request.user.is_authenticated:
        if app_config and app_config.get("join_url_name"):
            return redirect(app_config["join_url_name"])
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            if app_key:
                onboard_user_for_app(user, app_key)

                if app_config and app_config.get("post_register_url_name"):
                    return redirect(app_config["post_register_url_name"])

                if app_config and app_config.get("join_url_name"):
                    return redirect(app_config["join_url_name"])

            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = RegisterForm()

    context = {
        "form": form,
        "app_key": app_key,
        "app_label": app_config.get("label") if app_config else None,
    }
    return render(request, "p_auth/register.html", context)