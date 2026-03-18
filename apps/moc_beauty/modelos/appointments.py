from django.core.exceptions import ValidationError
from django.db import models

from .base import TimeStampedModel
from .people import Client, Employee
from .catalog import Service


class Appointment(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendiente"),
        (STATUS_CONFIRMED, "Confirmada"),
        (STATUS_COMPLETED, "Completada"),
        (STATUS_CANCELLED, "Cancelada"),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Cliente",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Empleado",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Servicio",
    )
    start_at = models.DateTimeField(verbose_name="Fecha y hora de inicio")
    end_at = models.DateTimeField(verbose_name="Fecha y hora de fin")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Estado",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ["-start_at"]

    def __str__(self):
        return f"{self.client} - {self.service} - {self.start_at:%d/%m/%Y %H:%M}"

    def clean(self):
        super().clean()

        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValidationError("La fecha/hora de fin debe ser posterior al inicio.")

        if self.employee and self.start_at and self.end_at and self.status != self.STATUS_CANCELLED:
            overlapping = Appointment.objects.filter(
                employee=self.employee,
                status__in=[self.STATUS_PENDING, self.STATUS_CONFIRMED, self.STATUS_COMPLETED],
                start_at__lt=self.end_at,
                end_at__gt=self.start_at,
            )

            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError("El empleado ya tiene una cita asignada en ese tramo horario.")