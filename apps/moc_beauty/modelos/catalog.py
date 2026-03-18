from django.core.validators import MinValueValidator
from django.db import models

from .base import TimeStampedModel


class ServiceCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Categoría de servicio"
        verbose_name_plural = "Categorías de servicio"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de producto"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(TimeStampedModel):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="services",
        verbose_name="Categoría",
    )
    name = models.CharField(max_length=150, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    duration_minutes = models.PositiveIntegerField(verbose_name="Duración (minutos)")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["name"]
        unique_together = [("category", "name")]

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Categoría",
    )
    name = models.CharField(max_length=150, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de venta",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    minimum_stock = models.PositiveIntegerField(default=0, verbose_name="Stock mínimo")
    is_consumable = models.BooleanField(default=False, verbose_name="Consumible")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["name"]
        unique_together = [("category", "name")]

    def __str__(self):
        return self.name