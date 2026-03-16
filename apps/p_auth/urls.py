from django.urls import path
from django.contrib.auth import views as auth_views
from .views import AppLoginView

urlpatterns = [
    path("login/", AppLoginView.as_view(), name="login"),
    path("login-to/<slug:app_key>/", AppLoginView.as_view(), name="app_login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]