# decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from dashboard.models import Level, Submenu, Userlevel

def user_has_permission(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Ambil path dari request untuk menentukan submenu secara dinamis
        path = request.path
        
        # Resolve path untuk mendapatkan informasi tentang view yang sedang diakses
        resolved_view = resolve(path)
        view_name = resolved_view.url_name
        
        # Cari submenu berdasarkan nama view
        try:
            submenu = Submenu.objects.get(submenu_link=view_name)
        except Submenu.DoesNotExist:
            raise PermissionDenied("Access to this page is not allowed.")

        # Cek hak akses pengguna berdasarkan submenu yang ditemukan
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("User is not authenticated.")

        try:
            user_level = Userlevel.objects.get(user_nama=user).userlevel
        except Userlevel.DoesNotExist:
            raise PermissionDenied("User level not found.")

        if submenu not in user_level.level_submenu.all():
            raise PermissionDenied("User does not have permission for this page.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
