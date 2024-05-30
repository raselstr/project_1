from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from ..models import Kegiatan
from ..forms import KegiatanForm

def list_kegiatan(request):
    data = Kegiatan.objects.all()
    form = KegiatanForm()
    context = {
        "judul": "Daftar Jenis Kegiatan", 
        "tombol" : "Tambah Jenis Kegiatan",
        "form": form, 
        "datas": data
    }
    return render(request, "kegiatan/kegiatan_list.html", context) 

def simpan_kegiatan(request):
    data = Kegiatan.objects.all()
    if request.method == "POST":
        form = KegiatanForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_kegiatan')
    else:
        form = KegiatanForm()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "kegiatan/kegiatan_list.html", context)

def update_kegiatan(request, pk):
    data = get_object_or_404(Kegiatan, id=pk)
    formupdate = KegiatanForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_kegiatan")
    else:
        formupdate = KegiatanForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Kegiatan"}
    return render(request, "kegiatan/kegiatan_edit.html", context)

def delete_kegiatan(request, pk):
    data = Kegiatan.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("list_kegiatan")
