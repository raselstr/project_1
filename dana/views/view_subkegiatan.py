from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from ..models import Subkegiatan, Kegiatan, Program
from ..forms import SubkegiatanForm, KegiatanForm

def list_subkegiatan(request):
    data = Subkegiatan.objects.all()
    form = SubkegiatanForm()
    context = {
        "judul": "Daftar Jenis Subkegiatan", 
        "tombol" : "Tambah Jenis Subkegiatan",
        "form": form, 
        "datas": data
    }
    return render(request, "subkegiatan/subkegiatan_list.html", context) 

def simpan_subkegiatan(request):
    data = Subkegiatan.objects.all()
    if request.method == "POST":
        form = SubkegiatanForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_subkegiatan')
    else:
        form = Subkegiatan()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "subkegiatan/subkegiatan_list.html", context)

def update_subkegiatan(request, pk):
    data = get_object_or_404(Subkegiatan, id=pk)
    formupdate = SubkegiatanForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_subkegiatan")
    else:
        formupdate = SubkegiatanForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update subkegiatan"}
    return render(request, "subkegiatan/subkegiatan_edit.html", context)

def delete_subkegiatan(request, pk):
    data = Subkegiatan.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("list_subkegiatan")

def load_program(request):
    dana_id = request.GET.get('subkegiatan_dana')
    programs = Program.objects.filter(program_dana=dana_id)

    return render(request, "subkegiatan/load_dana.html", {'programs':programs})