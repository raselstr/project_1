from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from collections import defaultdict
from django.contrib import messages

from . models import Penerimaan
from . forms import PenerimaanForm

Form_data = PenerimaanForm
Model_data = Penerimaan
lokasitemplate = 'penerimaan/penerimaan_list.html'
lokasiupdate = 'penerimaan/penerimaan_edit.html'
tag_url = 'list_penerimaan'

def list(request):
    
    data = Model_data.objects.all().order_by('penerimaan_dana')
    form = Form_data(request.POST or None)
    
    subtotals = defaultdict(lambda: 0)
    total = 0
    
    for item in data:
        subtotals[item.penerimaan_dana] += item.penerimaan_nilai
        total += item.penerimaan_nilai

    subtotal_list = [{'dana': dana, 'subtotal': subtotal} for dana, subtotal in subtotals.items()]
    
    context = {
        "judul": "Daftar Penerimaan Dana", 
        "tombol" : "Tambah Penerimaan",
        "form": form, 
        "datas": data,
        "subtotal_list": subtotal_list,
        "total": total,
        
    }
    return render(request, lokasitemplate, context) 

def simpan(request):
    if request.method == "POST":
        form = Form_data(request.POST or None)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Data Berhasil disimpan')
                return redirect(tag_url)
            except ValidationError as e:
                form.add_error(None, e.message)
                messages.error(request, e.message)
    else:
        form = Form_data()
    context = {
        'form'  : form,
    }
    # print(messages.error)
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
    return render(request, lokasiupdate, context)

def delete(request, pk):
    data = Model_data.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect(tag_url)


