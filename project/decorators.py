from functools import wraps
from django.shortcuts import HttpResponse
from dashboard.models import Userlevel

def menu_access_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Periksa apakah pengguna terautentikasi
        if not request.user.is_authenticated:
            return HttpResponse("Unauthorized", status=401)
        
        # Ambil level pengguna dari model Userlevel
        try:
            user_level = Userlevel.objects.get(user_nama=request.user)
        except Userlevel.DoesNotExist:
            return HttpResponse("Unauthorized", status=401)
        
        # Dapatkan semua submenu yang diizinkan untuk level pengguna
        allowed_submenus = user_level.userlevel.level_submenu.all()

        # Lanjutkan hanya jika submenu dari request ada di dalam allowed_submenus
        submenu_id = request.GET.get('submenu_id')
        if submenu_id and int(submenu_id) in allowed_submenus.values_list('id', flat=True):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse("Unauthorized", status=401)

    return wrapper
