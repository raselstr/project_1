from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Pagudausg
from .forms import PagudausgForm

Form_data = PagudausgForm
Model_data = Pagudausg
lokasitemplate = 'pagu/pagu_list.html'
lokasiupdate = 'pagu/pagu_edit.html'
tag_url = 'list_pagudausg'

def list(request):
    
    data = Model_data.objects.all().order_by('pagudausg_dana')
    form = Form_data(request.POST or None)
    context = {
        "judul": "Daftar Pagu TKDD", 
        "tombol" : "Tambah Pagu TKDD",
        "datas": data,
        'form': form,
    }
    return render(request, lokasitemplate, context) 

def simpan(request):
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

    context = {"form": formupdate, "datas": data,"judul": "Update Pagu"}
    return render(request, lokasiupdate, context)

def delete(request, pk):
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url)


