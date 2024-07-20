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

            # Dapatkan semua Levelsub yang diizinkan untuk level pengguna
            allowed_levelsubs = Levelsub.objects.filter(levelsub_level=user_level)
            
            # Dapatkan ID submenu yang relevan dari URL atau view args
            submenu_id = kwargs.get('submenu_id')  # Asumsi ada submenu_id di URL
            if submenu_id:
                # Filter levelsub yang relevan untuk submenu ini
                levelsubs_for_submenu = allowed_levelsubs.filter(submenu=submenu_id)

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
                status_check = any(getattr(levelsub, permission_field) for levelsub in levelsubs_for_submenu)

                # Print dan log status permission
                print(f"Permission field checked: {permission_field} - Status: {status_check}")

                if not status_check:
                    logger.warning(f"Pengguna {user} tidak memiliki izin {permission} untuk submenu {submenu_id}.")
                    return HttpResponseForbidden(f"Anda tidak memiliki akses untuk {permission} data.")

            else:
                logger.error("submenu_id tidak ditemukan dalam URL atau args.")
                return HttpResponseForbidden("Tidak ditemukan submenu ID.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

