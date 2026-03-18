from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .decorators import mb_role_required
from .models import MBRole, MBMembership

# =========================
# Frontoffice
# =========================
def public_home(request):
    return render(request, "moc_beauty/public_home.html")


def quienes_somos(request):
    return render(request, "moc_beauty/quienes_somos.html")


def productos(request):
    return render(request, "moc_beauty/productos.html")


def servicios(request):
    return render(request, "moc_beauty/servicios.html")


@login_required
def pedir_cita(request):
    return render(request, "moc_beauty/pedir_cita.html")


def aviso_legal(request):
    return render(request, "moc_beauty/aviso_legal.html")


def privacidad(request):
    return render(request, "moc_beauty/privacidad.html")


def cookies(request):
    return render(request, "moc_beauty/cookies.html")


def contacto(request):
    return render(request, "moc_beauty/contacto.html")

# =========================
# Login/Registro
# =========================
def login_redirect(request):
    return redirect("p_auth:app_login", app_key="moc_beauty")


def register_redirect(request):
    return redirect("p_auth:app_register", app_key="moc_beauty")


@mb_role_required("ADMIN", "EMPLEADO")
def dashboard(request):
    return render(request, "moc_beauty/dashboard.html")


@login_required
def join(request):
    role = MBRole.objects.get(code="CLIENTE")
    MBMembership.objects.get_or_create(
        user=request.user,
        role=role,
        defaults={"active": True},
    )
    return redirect("moc_beauty:pedir_cita")

# =========================
# Backoffice
# =========================

@mb_role_required("ADMIN", "EMPLEADO")
def agenda(request):
    return render(request, "moc_beauty/bo/agenda.html")

@mb_role_required("ADMIN", "EMPLEADO")
def clientes_list(request):
    return render(request, "moc_beauty/bo/clientes_list.html")

@mb_role_required("ADMIN", "EMPLEADO")
def cliente_detail(request):
    return render(request, "moc_beauty/bo/cliente_detail.html")

@mb_role_required("ADMIN", "EMPLEADO")
def servicios_list(request):
    return render(request, "moc_beauty/bo/servicios_list.html")

@mb_role_required("ADMIN", "EMPLEADO")
def empleados_list(request):
    return render(request, "moc_beauty/bo/empleados_list.html")

@mb_role_required("ADMIN", "EMPLEADO")
def configuracion(request):
    return render(request, "moc_beauty/bo/configuracion.html")

