from apps.moc_beauty.models import MBMembership

def has_mb_role(user, role_code: str) -> bool:
    if not user.is_authenticated:
        return False
    return MBMembership.objects.filter(user=user, role__code=role_code, active=True).exists()

