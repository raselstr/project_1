import logging
from functools import wraps
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from dashboard.models import Userlevel, Levelsub

logger = logging.getLogger(__name__)

def menu_access_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # Cek otentikasi
            if not user.is_authenticated:
                return HttpResponseRedirect(reverse('notfound'))

            # Jika user adalah superuser, lewati pengecekan
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            try:
                user_level = Userlevel.objects.get(user_nama=user).userlevel
            except Userlevel.DoesNotExist:
                logger.warning(f"Pengguna {user} tidak memiliki level pengguna yang ditetapkan.")
                return HttpResponseRedirect(reverse('notfound'))

            # Dapatkan semua levelsub yang diizinkan untuk level pengguna
            allowed_levelsubs = Levelsub.objects.filter(levelsub_level=user_level)

            # Periksa menu akses
            if not allowed_levelsubs.filter(lihat=True).exists():
                return HttpResponseRedirect(reverse('notfound'))

            # Peta permission
            permission_map = {
                'list': 'lihat',
                'simpan': 'simpan',
                'update': 'edit',
                'delete': 'hapus'
            }

            if permission not in permission_map:
                logger.error(f"Permission tidak valid: {permission}")
                return HttpResponseForbidden("Permission tidak dikenali.")

            permission_field = permission_map[permission]
            status_check = any(getattr(levelsub, permission_field) for levelsub in allowed_levelsubs)

            # Print dan log status permission
            print(f"Permission field checked: {permission_field} - Status: {status_check}")

            if not status_check:
                logger.warning(f"Pengguna {user} tidak memiliki izin {permission}.")
                return HttpResponseForbidden(f"Anda tidak memiliki akses untuk {permission} data.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
