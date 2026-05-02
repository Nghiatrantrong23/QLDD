from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_required(view_func):
    """
    Decorator cho các view yêu cầu quyền superuser (Admin).
    Nếu không phải admin, trả về lỗi 403 Forbidden.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
