from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..utils import dataprogram
from ..models import Kegiatan, Program
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

def load_program(request):
    return dataprogram(
        request, 
        'kegiatan_dana','Program',
        'program_dana',
        'load/load_program.html')

# def load_dana(request):
#     dana_id = request.GET.get('kegiatan_dana')
#     programs = Program.objects.filter(program_dana=dana_id)
#     print(programs)

#     return render(request, "load/load_dana.html", {'programs':programs})