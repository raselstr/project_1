from django.urls import reverse, NoReverseMatch
from dashboard.models import Menu, Submenu

def menu_context_processor(request):
    if request.user.is_authenticated:
        if request.session.get('is_superuser', False):
            # Jika superuser, ambil semua menu dan submenu
            menus = Menu.objects.all()
            submenu_dict = {menu: Submenu.objects.filter(submenu_menu=menu) for menu in menus}
        else:
            # Jika bukan superuser, ambil menu dan submenu berdasarkan level user
            submenus_ids = request.session.get('submenus', [])
            submenus = Submenu.objects.filter(id__in=submenus_ids)
            menus = Menu.objects.filter(id__in=submenus.values_list('submenu_menu', flat=True))
            submenu_dict = {menu: submenus.filter(submenu_menu=menu) for menu in menus}
        context = {
            "menus": menus,
            "submenu_dict": submenu_dict,
            "is_superuser": request.session.get('is_superuser', False),
            "user_nama": request.session.get('user_nama', 'Admin'),
            "subopd": request.session.get('subopd', 'Tidak Terikat'),
            "level": request.session.get('level', 'Super Admin'),
        }
    else:
        context = {
            "menus": Menu.objects.none(),
            "submenu_dict": {},
            "is_superuser": False,
            "user_nama": '',
            "subopd": '',
            "level": '',
        }
    
    return context

# def menu_context_processor(request):
#     menus = Menu.objects.all()
#     submenu_dict = {
#         menu: Submenu.objects.filter(submenu_menu=menu) for menu in menus}
#     return {
#         "menus": menus,
#         "submenu_dict": submenu_dict,
#     }




# def menu_context_processor(request):
#     menus = Menu.objects.all()
#     submenu_dict = {}

#     for menu in menus:
#         submenus = Submenu.objects.filter(submenu_menu=menu)
#         for submenu in submenus:
#             try:
#                 if not submenu.submenu_link:
#                     # Jika submenu tidak memiliki link, kita atur URL-nya ke dashboard
#                     submenu.submenu_link = reverse('dashboard')
#                 else:
#                     # Coba untuk mengakses URL pattern
#                     reverse(submenu.submenu_link)
#             except NoReverseMatch:
#                 # Jika tidak ada URL pattern yang cocok, atur URL ke dashboard
#                 submenu.link = reverse('dashboard')
#         submenu_dict[menu] = submenus

#     return {
#         "menus": menus,
#         "submenu_dict": submenu_dict,
#     }

