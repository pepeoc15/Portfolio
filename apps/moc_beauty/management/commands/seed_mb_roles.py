from django.core.management.base import BaseCommand
from apps.moc_beauty.models import MBRole

class Command(BaseCommand):
    help = "Crea roles base de moc_beauty"

    def handle(self, *args, **options):
        roles = [
            ("ADMIN", "Admin"),
            ("EMPLEADO", "Empleado"),
            ("CLIENTE", "Cliente"),
        ]
        for code, name in roles:
            MBRole.objects.get_or_create(code=code, defaults={"name": name})
        self.stdout.write(self.style.SUCCESS("Roles moc_beauty creados/ya existentes."))
