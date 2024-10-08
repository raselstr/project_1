from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session

from ..models import Userlevel
from ..forms import UserlevelForm

@set_submenu_session
@menu_access_required('list')
def list_userlevel(request):
    request.session['next'] = request.get_full_path()
    data = Userlevel.objects.all()
    form = UserlevelForm()
    context = {
        "judul": "Daftar User Level", 
        "tombol" : "Tambah User Level",
        "form": form, 
        "datas": data
    }
    return render(request, "userlevel/userlevel_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan_userlevel(request):
    request.session['next'] = request.get_full_path()
    data = Userlevel.objects.all()
    if request.method == "POST":
        form = UserlevelForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_userlevel')
    else:
        form = UserlevelForm()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "userlevel/userlevel_list.html", context)

@set_submenu_session
@menu_access_required('update')
def update_userlevel(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Userlevel, id=pk)
    formupdate = UserlevelForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_userlevel")
    else:
        formupdate = UserlevelForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update User Level"}
    return render(request, "userlevel/userlevel_edit.html", context)

@set_submenu_session
@menu_access_required('delete')
def delete_userlevel(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Userlevel.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Userlevel.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_userlevel")
