from datetime import datetime
from django.urls import reverse, NoReverseMatch
from dashboard.models import Menu, Submenu
from dankel.models import RencDankeljadwal

def menu_context_processor(request):
    
    # Menyimpan tahun saat ini ke dalam session
    current_year = datetime.now().year
    request.session['tahun'] = current_year
    try:
        tblrencana=RencDankeljadwal.objects.latest('rencdankel_jadwal')
        jadwal = tblrencana.rencdankel_jadwal
    except RencDankeljadwal.DoesNotExist:
        jadwal = 1
    
    if request.user.is_authenticated:
        if request.session.get('is_superuser', False):
            menus = Menu.objects.all()
            submenu_dict = {menu: Submenu.objects.filter(submenu_menu=menu) for menu in menus}
        else:
            submenus_ids = request.session.get('submenus', [])
            submenus = Submenu.objects.filter(id__in=submenus_ids)
            menus = Menu.objects.filter(id__in=submenus.values_list('submenu_menu', flat=True))
            submenu_dict = {menu: submenus.filter(submenu_menu=menu) for menu in menus}

            # # Simpan submenu_id dalam session
            # if submenus.exists():
            #     request.session['current_submenu_id'] = submenus.first().id
            # else:
            #     request.session['current_submenu_id'] = None

        context = {
            "menus": menus,
            "submenu_dict": submenu_dict,
            "is_superuser": request.session.get('is_superuser', False),
            "user_nama": request.session.get('user_nama', 'Super'),
            "subopd": request.session.get('subopd', 'Tidak Terikat'),
            "level": request.session.get('level', 'Super Admin'),
            "tahun": request.session.get('tahun', current_year),
            "jadwal": request.session.get('jadwal',jadwal),
            "idsubopd" : request.session.get('idsubopd','None'),
        }
    else:
        context = {
            "menus": Menu.objects.none(),
            "submenu_dict": {},
            "is_superuser": False,
            "user_nama": '',
            "subopd": '',
            "level": '',
            "tahun": current_year,
            "jadwal":'',
            "idsubopd":'',
        }
    
    return context
