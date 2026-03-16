from django.urls import path
from . import views

app_name = "moc_beauty"

urlpatterns = [
    path("", views.public_home, name="public_home"),
    path("quienes-somos/", views.quienes_somos, name="quienes_somos"),
    path("productos/", views.productos, name="productos"),
    path("servicios/", views.servicios, name="servicios"),
    path("pedir-cita/", views.pedir_cita, name="pedir_cita"),
    path("aviso-legal/", views.aviso_legal, name="aviso_legal"),
    path("privacidad/", views.privacidad, name="privacidad"),
    path("cookies/", views.cookies, name="cookies"),
    path("contacto/", views.contacto, name="contacto"),

    path("login/", views.login_redirect, name="login_redirect"),
    path("registrarse/", views.register, name="register"),
    path("unirse/", views.join, name="join"),
    path("dashboard/", views.dashboard, name="dashboard"),
]