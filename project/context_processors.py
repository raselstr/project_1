from datetime import datetime
from django.urls import reverse, NoReverseMatch
from dashboard.models import Menu, Submenu
from jadwal.models import Jadwal

def menu_context_processor(request):
    tahun = request.session.get('tahun')
    tbljadwal=Jadwal.objects.filter(jadwal_tahun=tahun, jadwal_aktif=True).last()
    if tbljadwal:
        jadwal_id = tbljadwal.id
        jadwal_keterangan = tbljadwal.jadwal_keterangan
    else:
        jadwal_id = 0
        jadwal_keterangan = "Tidak ada jadwal"
    
    session_jadwal = request.session.get('jadwal')
    if session_jadwal != jadwal_id:
        request.session['jadwal'] = jadwal_id
        request.session['jadwal_ket'] = jadwal_keterangan
        request.session.modified = True
    
    
    if request.user.is_authenticated:
        if request.session.get('is_superuser', False):
            menus = Menu.objects.all()
            submenu_dict = {menu: Submenu.objects.filter(submenu_menu=menu) for menu in menus}
        else:
            submenus_ids = request.session.get('submenus', [])
            submenus = Submenu.objects.filter(id__in=submenus_ids)
            menus = Menu.objects.filter(id__in=submenus.values_list('submenu_menu', flat=True))
            submenu_dict = {menu: submenus.filter(submenu_menu=menu) for menu in menus}

        context = {
            "menus": menus,
            "submenu_dict": submenu_dict,
            "is_superuser": request.session.get('is_superuser', False),
            "user_nama": request.session.get('user_nama', 'Super'),
            "subopd": request.session.get('subopd', 'Tidak Terikat'),
            "level": request.session.get('level', 'Super Admin'),
            "tahun": tahun,
            "jadwal": jadwal_id,
            "jadwal_ket": jadwal_keterangan,
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
            "tahun": tahun,
            "jadwal":'',
            "jadwal_ket":'Tidak ada jadwal',
            "idsubopd":'',
        }
    
    return context
