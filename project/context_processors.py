from django.urls import reverse, NoReverseMatch
from dashboard.models import Menu, Submenu


def menu_context_processor(request):
    menus = Menu.objects.all()
    submenu_dict = {
        menu: Submenu.objects.filter(submenu_menu=menu) for menu in menus}
    return {
        "menus": menus,
        "submenu_dict": submenu_dict,
    }




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

