from django.shortcuts import render, redirect
from django.contrib import messages

from ..models import Menu
from ..forms import Menuform

def list_menu(request):
    data = Menu.objects.all()
    form = Menuform()
    context = {
        "judul": "Daftar Menu", 
        "tombol" : "Tambah Menu",
        "link" : "menu_list",
        "form": form, 
        "datas": data
    }
    return render(request, "menu/menu_list.html", context) 

def simpan_menu(request):
    data = Menu.objects.all()
    if request.method == "POST":
        form = Menuform(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_menu')
    else:
        form = Menuform()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "menu/menu_list.html", context)

def delete_menu(request, pk):
    data = Menu.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("list_menu")
