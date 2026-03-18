from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .modelos import SaleItem


@receiver(post_save, sender=SaleItem)
@receiver(post_delete, sender=SaleItem)
def update_sale_total(sender, instance, **kwargs):
    sale = instance.sale
    sale.recalculate_total()
    sale.save(update_fields=["total"])