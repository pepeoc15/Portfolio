from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from apps.moc_beauty.services.authz import has_mb_role
from django.shortcuts import redirect

def mb_role_required(*role_codes):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("p_auth:app_login", app_key="moc_beauty")
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if any(has_mb_role(request.user, code) for code in role_codes):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped
    return decorator
