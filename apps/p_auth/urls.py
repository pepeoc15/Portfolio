from django.urls import path
from .views import AppLoginView, AppLogoutView

urlpatterns = [
    path("login/", AppLoginView.as_view(), name="login"),
    path("login/<slug:app_key>/", AppLoginView.as_view(), name="app_login"),
    path("logout/", AppLogoutView.as_view(), name="logout"),
    path("logout/<slug:app_key>/", AppLogoutView.as_view(), name="app_logout"),
]