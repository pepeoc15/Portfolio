from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .decorators import mb_role_required

from .forms import MBRegisterForm
from .models import MBRole, MBMembership

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

def login_redirect(request):
    return redirect("login")  # el login global (p_auth) si name="login"

@mb_role_required("ADMIN", "EMPLEADO")
def dashboard(request):
    return render(request, "moc_beauty/dashboard.html")


def register(request):
    # Si ya está logueado, que use "join" (no crear otra cuenta)
    if request.user.is_authenticated:
        return redirect("moc_beauty:join")

    if request.method == "POST":
        form = MBRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            role = MBRole.objects.get(code="CLIENTE")
            MBMembership.objects.get_or_create(user=user, role=role, defaults={"active": True})

            # login automático tras registrarse
            login(request, user)

            return redirect("moc_beauty:public_home")
    else:
        form = MBRegisterForm()

    return render(request, "moc_beauty/register.html", {"form": form})


@login_required
def join(request):
    role = MBRole.objects.get(code="CLIENTE")
    MBMembership.objects.get_or_create(user=request.user, role=role, defaults={"active": True})
    return redirect("moc_beauty:public_home")
