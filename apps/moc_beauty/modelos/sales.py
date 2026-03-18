from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.manager import RelatedManager


from .base import TimeStampedModel
from .people import Client, Employee
from .catalog import Product, Service


class Sale(TimeStampedModel):
    items: RelatedManager["SaleItem"]


    STATUS_DRAFT = "draft"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    PAYMENT_CASH = "cash"
    PAYMENT_CARD = "card"
    PAYMENT_TRANSFER = "transfer"
    PAYMENT_BIZUM = "bizum"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Borrador"),
        (STATUS_COMPLETED, "Completada"),
        (STATUS_CANCELLED, "Cancelada"),
    ]

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_CASH, "Efectivo"),
        (PAYMENT_CARD, "Tarjeta"),
        (PAYMENT_TRANSFER, "Transferencia"),
        (PAYMENT_BIZUM, "Bizum"),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
        verbose_name="Cliente",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="sales",
        verbose_name="Empleado",
    )
    sale_date = models.DateTimeField(verbose_name="Fecha de venta")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name="Estado",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        verbose_name="Forma de pago",
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        verbose_name="Total",
    )
    notes = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-sale_date", "-id"]

    def __str__(self):
        return f"Venta #{self.pk} - {self.sale_date:%d/%m/%Y %H:%M}"

    def recalculate_total(self):
        total = sum((item.subtotal for item in self.items.all()), Decimal("0.00"))
        self.total = total
        return total


class SaleItem(TimeStampedModel):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Venta",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sale_items",
        verbose_name="Producto",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sale_items",
        verbose_name="Servicio",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio unitario",
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Subtotal",
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Línea de venta"
        verbose_name_plural = "Líneas de venta"

    def __str__(self):
        if self.product:
            item_name = self.product.name
        elif self.service:
            item_name = self.service.name
        else:
            item_name = "Ítem sin definir"
        return f"{item_name} x{self.quantity}"

    def clean(self):
        super().clean()

        if not self.product and not self.service:
            raise ValidationError("Debe indicar un producto o un servicio.")

        if self.product and self.service:
            raise ValidationError("Una línea no puede tener producto y servicio a la vez.")

    def save(self, *args, **kwargs):
        self.full_clean()
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)