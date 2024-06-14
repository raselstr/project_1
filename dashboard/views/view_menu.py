from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError

from ..models import Menu
from ..forms import Menuform

def list_menu(request):
    data = Menu.objects.all()
    form = Menuform()
    context = {
        "judul": "Daftar Menu", 
        "tombol" : "Tambah Menu",
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

def update_menu(request, pk):
    data = get_object_or_404(Menu, id=pk)
    formupdate = Menuform(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_menu")
    else:
        formupdate = Menuform(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Menu"}
    return render(request, "menu/menu_edit.html", context)

def delete_menu(request, pk):
    try:
        data = Menu.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Menu.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_menu")
