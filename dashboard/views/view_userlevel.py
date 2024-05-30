from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from ..models import Userlevel
from ..forms import UserlevelForm

def list_userlevel(request):
    data = Userlevel.objects.all()
    form = UserlevelForm()
    context = {
        "judul": "Daftar User Level", 
        "tombol" : "Tambah User Level",
        "form": form, 
        "datas": data
    }
    return render(request, "userlevel/userlevel_list.html", context) 

def simpan_userlevel(request):
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

def update_userlevel(request, pk):
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

def delete_userlevel(request, pk):
    data = Userlevel.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("list_userlevel")
