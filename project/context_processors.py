from dashboard.models import Menu, Submenu

def menu_context_processor(request):
    menus = Menu.objects.all()
    submenu_dict = {menu: Submenu.objects.filter(submenu_menu=menu) for menu in menus}
    return {
        "menus": menus,
        "submenu_dict": submenu_dict,
    }
