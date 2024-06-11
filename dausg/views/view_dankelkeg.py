from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from dana.utils import datasubrinc

from ..models import DankelKeg, DankelProg
from ..forms import DankelKegForm

Form_data = DankelKegForm
Model_data = DankelKeg
Model_induk = DankelProg
lokasitemplate = 'dankelkeg/dankelkeg_list.html'
lokasiupdate = 'dankelkeg/dankelkeg_edit.html'
tag_url = 'list_dankelkeg'
lokasiload = 'load/load_subrinckeg.html'

def list(request, number):
    
    dankel_prog = get_object_or_404(Model_induk, id=number)
    data = dankel_prog.dankelkegs.prefetch_related('dankelsubs').all()
    # data = Model_data.objects.all()
    form = Form_data()
    
    context = {
        "judul": "Daftar Kegiatan", 
        'dankel_prog': dankel_prog,
        "tombol" : "Tambah Kegiatan",
        "form": form, 
        "datas": data,
        "number":number,
        
    }
    return render(request, lokasitemplate, context) 

def simpan(request, number):
    if request.method == "POST":
        form = Form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url, number=number)
    else:
        form = Form_data()
    context = {
        'form'  : form,
    }
    return render(request, lokasitemplate, context)

def update(request, number, pk):
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url, number=number)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "number": number, "judul": "Update Kegiatan"}
    return render(request, lokasiupdate, context)

def delete(request, number, pk):
    data = Model_data.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect(tag_url, number=number)


