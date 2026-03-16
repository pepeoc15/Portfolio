from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from apps.moc_beauty.services.authz import has_mb_role

def mb_role_required(*role_codes):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if any(has_mb_role(request.user, code) for code in role_codes):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped
    return decorator
