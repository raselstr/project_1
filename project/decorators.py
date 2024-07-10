from functools import wraps
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponseForbidden
from dashboard.models import Userlevel
from django.urls import reverse

def menu_access_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Periksa apakah pengguna terautentikasi
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('notfound'))
        
        # Cek apakah pengguna adalah superuser
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Ambil level pengguna dari model Userlevel
        try:
            user_level = Userlevel.objects.get(user_nama=request.user)
        except Userlevel.DoesNotExist:
            return HttpResponseRedirect(reverse('notfound'))
        
        # Dapatkan semua submenu yang diizinkan untuk level pengguna
        allowed_submenus = user_level.userlevel.level_submenu.all()

        # Lanjutkan hanya jika submenu dari request ada di dalam allowed_submenus
        submenu_id = request.GET.get('submenu_id')
        if submenu_id and int(submenu_id) in allowed_submenus.values_list('id', flat=True):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('notfound'))

    return wrapper

def check_permissions(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")

        try:
            user_level = Userlevel.objects.get(user_nama=user).userlevel
        except Userlevel.DoesNotExist:
            return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
        
        # Check list_data and simpan_data permissions
        if kwargs.get('permission') == 'list_data' and not user_level.list_data:
            return HttpResponseForbidden("Anda tidak memiliki akses untuk melihat data.")
        if kwargs.get('permission') == 'simpan_data' and not user_level.simpan_data:
            return HttpResponseForbidden("Anda tidak memiliki akses untuk menyimpan data.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
