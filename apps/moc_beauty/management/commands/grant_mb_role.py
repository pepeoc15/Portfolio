from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.moc_beauty.models import MBRole, MBMembership

User = get_user_model()

class Command(BaseCommand):
    help = "Asigna un rol de moc_beauty a un usuario"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("role_code")

    def handle(self, *args, **options):
        username = options["username"]
        role_code = options["role_code"].upper()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError("Usuario no existe")

        try:
            role = MBRole.objects.get(code=role_code)
        except MBRole.DoesNotExist:
            raise CommandError("Rol no existe. Ejecuta seed_mb_roles primero.")

        MBMembership.objects.get_or_create(user=user, role=role)
        self.stdout.write(self.style.SUCCESS(f"Asignado {role_code} a {username}"))
