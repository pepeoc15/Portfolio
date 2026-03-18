from django.contrib import admin
from .models import MBRole, MBMembership, Client, Employee, Product, Service, Sale, SaleItem

admin.site.register(MBRole)
admin.site.register(MBMembership)
admin.site.register(Client)
admin.site.register(Employee)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(Sale)
admin.site.register(SaleItem)


admin.site.site_header = "Administración de Moc Beauty"
admin.site.index_title = "Panel de administración"
admin.site.site_title = "Moc Beauty Admin"

