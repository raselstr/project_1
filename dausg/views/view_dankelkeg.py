from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from dana.utils import datasubrinc

from ..models import DankelKeg
from ..forms import DankelKegForm

Form_data = DankelKegForm
Model_data = DankelKeg
lokasitemplate = 'dankelkeg/dankelkeg_list.html'
tag_url = 'list_dankelkeg'
lokasiload = 'load/load_subrinckeg.html'

def list(request):
    data = Model_data.objects.all()
    form = Form_data()
    context = {
        "judul": "Daftar Kegiatan", 
        "tombol" : "Tambah Kegiatan",
        "form": form, 
        "datas": data
    }
    return render(request, lokasitemplate, context) 

def simpan(request):
    data = Model_data.objects.all()
    if request.method == "POST":
        form = Form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url)
    else:
        form = Form_data()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, lokasitemplate, context)

def update(request, pk):
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Kegiatan"}
    return render(request, lokasitemplate, context)

def delete(request, pk):
    data = Model_data.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect(tag_url)

def load(request):
    kwargs = {
        'nama_app'  : 'dausg',
        'model_name' : Model_data,
        'fieldsmodel' : ['dankel_subrinc'],
        'template_name' : lokasiload,
        'fieldget' : 'dankelkeg_subrinc',
        
    }
    return datasubrinc(request, **kwargs)