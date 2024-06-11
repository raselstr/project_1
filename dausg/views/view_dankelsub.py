from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from dana.utils import datasubrinc

from ..models import DankelKeg,Dankelsub
from ..forms import DankelSubForm

Form_data = DankelSubForm
Model_data = Dankelsub
Model_induk = DankelKeg
lokasitemplate = 'dankelsub/dankelsub_list.html'
lokasiupdate = 'dankelsub/dankelsub_edit.html'
tag_url = 'list_dankelsub'

def list(request, number, sub):
    
    dankel_keg = get_object_or_404(Model_induk, id=sub)
    data = dankel_keg.dankelsubs.all()
    # data = Model_data.objects.all()
    form = Form_data()
    
    context = {
        "judul": "Daftar Kegiatan", 
        'dankel_keg': dankel_keg,
        "tombol" : "Tambah Kegiatan",
        "form": form, 
        "datas": data,
        "number":number,
        
    }
    return render(request, lokasitemplate, context) 

def simpan(request, sub):
    data = Model_data.objects.all()
    if request.method == "POST":
        form = Form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url, sub=sub)
    else:
        form = Form_data()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, lokasitemplate, context)

def update(request, number, sub, pk):
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url, number=number)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "number": number, "sub": sub, "judul": "Update Kegiatan"}
    return render(request, lokasiupdate, context)

def delete(request, number, sub, pk):
    data = Model_data.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect(tag_url, number=number, sub=sub)


