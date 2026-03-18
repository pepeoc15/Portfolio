from django.conf import settings
from django.db import models

from .base import TimeStampedModel


class Client(TimeStampedModel):
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Apellidos")
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Teléfono",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
        verbose_name="Email",
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Employee(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moc_beauty_employee",
        verbose_name="Usuario",
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    specialty = models.CharField(max_length=150, blank=True, verbose_name="Especialidad")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["user__first_name", "user__last_name", "user__username"]

    def __str__(self):
        full_name = self.user.get_full_name().strip()
        return full_name or self.user.username