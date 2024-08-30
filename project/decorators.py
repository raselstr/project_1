from functools import wraps
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from dashboard.models import Userlevel, Levelsub
import logging

logger = logging.getLogger(__name__)

def set_submenu_session(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        submenu_id = request.GET.get('submenu_id')
        if submenu_id:
            request.session['current_submenu_id'] = submenu_id
            # Redirect to remove query parameters from URL
            return redirect(request.path)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

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
            next_url = request.session.get('next')
            
            # Dapatkan ID submenu dari session
            submenu_id = request.session.get('current_submenu_id')
            if submenu_id:
                # Filter levelsub yang relevan untuk submenu ini
                levelsubs_for_submenu = allowed_levelsubs.filter(levelsub_submenu=submenu_id)

                # Peta permission
                permission_map = {
                    'list': 'lihat',
                    'simpan': 'simpan',
                    'update': 'edit',
                    'delete': 'hapus'
                }

                if permission not in permission_map:
                    logger.error(f"Permission tidak valid: {permission}")
                    messages.error(request, "Permission tidak dikenali.")
                    return redirect(next_url)

                permission_field = permission_map[permission]
                status_check = any(getattr(levelsub, permission_field) for levelsub in levelsubs_for_submenu)

                # Print dan log status permission
                # print(f"Permission field checked: {permission_field} - Status: {status_check} {levelsubs_for_submenu}")

                if not status_check:
                    logger.warning(f"Pengguna {user} tidak memiliki izin {permission} untuk submenu {submenu_id}.")
                    messages.error(request, f"Anda tidak memiliki akses untuk {permission} data.")
                    return redirect(next_url)
            else:
                logger.error("submenu_id tidak ditemukan dalam session.")
                messages.error(request, "Tidak ditemukan submenu ID dalam session.")
                return redirect(next_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
