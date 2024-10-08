from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session

from ..utils import dataprogram, datakegiatan
from ..models import Subkegiatan, Kegiatan, Program
from ..forms import SubkegiatanForm, KegiatanForm

@set_submenu_session
@menu_access_required('list')
def list_subkegiatan(request):
    request.session['next'] = request.get_full_path()
    data = Subkegiatan.objects.all()
    form = SubkegiatanForm()
    context = {
        "judul": "Daftar Jenis Subkegiatan", 
        "tombol" : "Tambah Jenis Subkegiatan",
        "form": form, 
        "datas": data
    }
    return render(request, "subkegiatan/subkegiatan_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan_subkegiatan(request):
    request.session['next'] = request.get_full_path()
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

@set_submenu_session
@menu_access_required('update')
def update_subkegiatan(request, pk):
    request.session['next'] = request.get_full_path()
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

@set_submenu_session
@menu_access_required('delete')
def delete_subkegiatan(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Subkegiatan.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Subkegiatan.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_subkegiatan")


def load_kegprogram(request):
    return dataprogram(
        request, 
        'sub_dana','Program',
        'program_dana',
        'load/load_program.html')


def load_kegiatan(request):
    kwargs = {
        'model_name' : 'Kegiatan',
        'fieldsmodel' : ['kegiatan_dana','kegiatan_program'],
        'template_name' : 'load/load_kegiatan.html',
        'fieldget1' : 'sub_dana',
        'fieldget2' : 'sub_prog'
        
    }
    return datakegiatan(request, **kwargs)
    
# def load_program(request):
#     dana_id = request.GET.get('subkegiatan_dana')
#     programs = Program.objects.filter(program_dana=dana_id)

#     return render(request, "subkegiatan/load_dana.html", {'programs':programs})