from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from ..models import Level
from ..forms import LevelForm

def list_level(request):
    data = Level.objects.all()
    form = LevelForm()
    context = {
        "judul": "Daftar Level", 
        "tombol" : "Tambah Level",
        "form": form, 
        "datas": data
    }
    return render(request, "level/level_list.html", context) 

def simpan_level(request):
    data = Level.objects.all()
    if request.method == "POST":
        form = LevelForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_level')
    else:
        form = LevelForm()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "level/level_list.html", context)

def update_level(request, pk):
    data = get_object_or_404(Level, id=pk)
    formupdate = LevelForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_level")
    else:
        formupdate = LevelForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Level"}
    return render(request, "level/level_edit.html", context)

def delete_level(request, pk):
    data = Level.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("list_level")