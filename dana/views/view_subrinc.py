from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..utils import dataprogram, datakegiatan, datasubkegiatan
from ..models import Subkegiatan, Kegiatan, Program, Subrinc
from ..forms import SubrincForm, KegiatanForm

def list_subrinc(request):
    data = Subrinc.objects.all()
    form = SubrincForm()
    context = {
        "judul": "Daftar Jenis subrinc", 
        "tombol" : "Tambah Jenis subrinc",
        "form": form, 
        "datas": data
    }
    return render(request, "subrinc/subrinc_list.html", context) 

def simpan_subrinc(request):
    data = Subrinc.objects.all()
    if request.method == "POST":
        form = SubrincForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_subrinc')
    else:
        form = Subrinc()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "subrinc/subrinc_list.html", context)

def update_subrinc(request, pk):
    data = get_object_or_404(Subrinc, id=pk)
    formupdate = SubrincForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_subrinc")
    else:
        formupdate = SubrincForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update subrinc"}
    return render(request, "subrinc/subrinc_edit.html", context)

def delete_subrinc(request, pk):
    data = Subrinc.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("list_subrinc")


def load_kegprogram(request):
    return dataprogram(
        request, 
        'subrinc_dana','Program',
        'program_dana',
        'load/load_program.html')

def load_kegiatan(request):
    kwargs = {
        'model_name' : 'Kegiatan',
        'fieldsmodel' : ['kegiatan_dana','kegiatan_program'],
        'template_name' : 'load/load_kegiatan.html',
        'fieldget1' : 'subrinc_dana',
        'fieldget2' : 'subrinc_prog'
        
    }
    return datakegiatan(request, **kwargs)

def load_subkegiatan(request):
    kwargs = {
        'model_name' : 'Subkegiatan',
        'fieldsmodel' : ['sub_dana','sub_prog','sub_keg'],
        'template_name' : 'load/load_subkegiatan.html',
        'fieldget1' : 'subrinc_dana',
        'fieldget2' : 'subrinc_prog',
        'fieldget3' : 'subrinc_keg'
        
    }
    return datasubkegiatan(request, **kwargs)
    
# def load_program(request):
#     dana_id = request.GET.get('subrinc_dana')
#     programs = Program.objects.filter(program_dana=dana_id)

#     return render(request, "subrinc/load_dana.html", {'programs':programs})