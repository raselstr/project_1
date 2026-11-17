from datetime import datetime
from django.urls import reverse, NoReverseMatch
from dashboard.models import Menu, Submenu, Rinciansubmenu
from jadwal.models import Jadwal

def menu_context_processor(request):
    tahun = request.session.get('tahun')
    tbljadwal = Jadwal.objects.filter(jadwal_tahun=tahun, jadwal_aktif=True).last()
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
    
    tahun_display = str(tahun) if tahun is not None else ""

    if request.user.is_authenticated:
        is_su = request.session.get('is_superuser', False) or getattr(request.user, 'is_superuser', False)
        
        if is_su:
            menus = list(Menu.objects.all().order_by('menu_urutan', 'id'))
            all_submenus = list(Submenu.objects.all().order_by('submenu_urutan', 'id'))
            all_rincians = list(Rinciansubmenu.objects.all().order_by('rinciansubmenu_urutan', 'id'))
        else:
            allowed_rincian_ids = request.session.get('submenus', [])
            all_rincians = list(Rinciansubmenu.objects.filter(id__in=allowed_rincian_ids).order_by('rinciansubmenu_urutan', 'id'))
            allowed_submenu_ids = set(r.rinciansubmenu_submenu_id for r in all_rincians)
            all_submenus = list(Submenu.objects.filter(id__in=allowed_submenu_ids).order_by('submenu_urutan', 'id'))
            allowed_menu_ids = set(s.submenu_menu_id for s in all_submenus)
            menus = list(Menu.objects.filter(id__in=allowed_menu_ids).order_by('menu_urutan', 'id'))

        sidebar_menu_list = []
        for menu in menus:
            menu_subs = [s for s in all_submenus if s.submenu_menu_id == menu.id]
            if not menu_subs:
                continue

            # Menentukan apakah menu ditampilkan sebagai multi-level (nested)
            # Menu 'DAU SG & Dana Kelurahan' (id 4) atau menu dengan lebih dari 1 submenu
            has_nested_structure = len(menu_subs) > 1 or menu.id == 4 or 'DAU SG' in menu.menu_nama

            if has_nested_structure:
                sub_list = []
                for s in menu_subs:
                    s_rincians = [r for r in all_rincians if r.rinciansubmenu_submenu_id == s.id]
                    if s_rincians:
                        sub_list.append({
                            'submenu': s,
                            'nama': s.submenu_nama,
                            'icon': s.submenu_icon or 'fas fa-folder',
                            'rincians': s_rincians,
                        })
                if sub_list:
                    sidebar_menu_list.append({
                        'is_nested': True,
                        'menu': menu,
                        'menu_nama': menu.menu_nama,
                        'menu_icon': menu.menu_icon,
                        'sub_list': sub_list,
                    })
            else:
                # Menu standar dengan daftar rincian langsung (2-level: Menu -> Rincian)
                single_sub = menu_subs[0]
                s_rincians = [r for r in all_rincians if r.rinciansubmenu_submenu_id == single_sub.id]
                if s_rincians:
                    sidebar_menu_list.append({
                        'is_nested': False,
                        'menu': menu,
                        'menu_nama': menu.menu_nama,
                        'menu_icon': menu.menu_icon,
                        'rincians': s_rincians,
                    })

        context = {
            "menus": menus,
            "submenu_dict": {m: [r for r in all_rincians if r.rinciansubmenu_submenu.submenu_menu_id == m.id] for m in menus},
            "sidebar_menu_list": sidebar_menu_list,
            "is_superuser": is_su,
            "user_nama": request.session.get('user_nama', 'Super'),
            "subopd": request.session.get('subopd', 'Tidak Terikat'),
            "level": request.session.get('level', 'Super Admin'),
            "tahun": tahun_display,
            "jadwal": jadwal_id,
            "jadwal_ket": jadwal_keterangan,
            "idsubopd": request.session.get('idsubopd', 'None'),
        }
    else:
        context = {
            "menus": Menu.objects.none(),
            "submenu_dict": {},
            "sidebar_menu_list": [],
            "is_superuser": False,
            "user_nama": '',
            "subopd": '',
            "level": '',
            "tahun": tahun_display,
            "jadwal": '',
            "jadwal_ket": 'Tidak ada jadwal',
            "idsubopd": '',
        }
    
    return context
