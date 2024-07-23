from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session


from ..models import Submenu
from ..forms import SubmenuForm

@set_submenu_session
@menu_access_required('list')
def list_submenu(request):
    request.session['next'] = request.get_full_path()
    data = Submenu.objects.all()
    form = SubmenuForm()
    context = {
        "judul": "Daftar SubMenu", 
        "tombol" : "Tambah SubMenu",
        "form": form, 
        "datas": data
    }
    return render(request, "submenu/submenu_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan_submenu(request):
    request.session['next'] = request.get_full_path()
    data = Submenu.objects.all()
    if request.method == "POST":
        form = SubmenuForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_submenu')
    else:
        form = SubmenuForm()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "submenu/submenu_list.html", context)

@set_submenu_session
@menu_access_required('update')
def update_submenu(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Submenu, id=pk)
    formupdate = SubmenuForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_submenu")
    else:
        formupdate = SubmenuForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update SubMenu"}
    return render(request, "submenu/submenu_edit.html", context)

@set_submenu_session
@menu_access_required('delete')
def delete_submenu(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Submenu.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Submenu.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_submenu")
