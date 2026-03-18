from django.conf import settings
from django.db import models

from .base import TimeStampedModel


class MBRole(TimeStampedModel):
    ADMIN = "admin"
    EMPLOYEE = "employee"

    ROLE_CHOICES = [
        (ADMIN, "Administrador"),
        (EMPLOYEE, "Empleado"),
    ]

    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES, verbose_name="Nombre")
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    


    class Meta(TimeStampedModel.Meta):
        verbose_name = "Rol Moc Beauty"
        verbose_name_plural = "Roles Moc Beauty"
        ordering = ["name"]

    
    def __str__(self):
        return self.get_name_display() if self.name else self.name # type: ignore


class MBMembership(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moc_beauty_memberships",
        verbose_name="Usuario",
    )
    role = models.ForeignKey(
        MBRole,
        on_delete=models.PROTECT,
        related_name="memberships",
        verbose_name="Rol",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Asignación de rol Moc Beauty"
        verbose_name_plural = "Asignaciones de rol Moc Beauty"
        ordering = ["user__username", "role__name"]
        unique_together = [("user", "role")]

    def __str__(self):
        return f"{self.user} - {self.role}"