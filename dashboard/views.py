from django.shortcuts import render
from .models import Menu, Submenu

def index(request):
    menus = Menu.objects.all()  # Ambil semua objek menu
    submenu_dict = {}
    for menu in menus:
        submenus = Submenu.objects.filter(submenu_menu=menu)
        submenu_dict[menu] = submenus
    
    context = {
        'judul' : 'Dashboard',
        'menu' : menus,
        'submenu_dict' : submenu_dict
    }
    print(submenu_dict)
    # if request.method == "GET":
    return render(request, "dashboard/dashboard.html", context)

    
