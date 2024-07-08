from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from collections import defaultdict
from django.contrib import messages

from .. models import Penerimaan, DistribusiPenerimaan
from .. forms import PenerimaanForm

Form_data = PenerimaanForm
Model_data = Penerimaan
lokasitemplate = 'penerimaan/penerimaan_list.html'
lokasiupdate = 'penerimaan/penerimaan_edit.html'
tag_url = 'list_penerimaan'

def list(request):
    
    data = Model_data.objects.all().order_by('penerimaan_dana')
    form = Form_data(request.POST or None)
    
    subtotals = defaultdict(lambda: 0)
    distribusi_totals = defaultdict(lambda: 0)
    total = 0
    
    distribusi_data = DistribusiPenerimaan.objects.values('distri_penerimaan').annotate(total=Sum('distri_nilai'))
    for distribusi in distribusi_data:
        distribusi_totals[distribusi['distri_penerimaan']] = distribusi['total']

    penerimaan_list = []
    
    for item in data:
        subtotals[item.penerimaan_dana] += item.penerimaan_nilai
        total += item.penerimaan_nilai
        
        penerimaan_list.append({
            'penerimaan': item,
            'total_distribusi': distribusi_totals.get(item.id, 0)
        })

    # subtotal_list = [{'dana': dana, 'subtotal': subtotal} for dana, subtotal in subtotals.items()]
    
    context = {
        "judul": "Daftar Penerimaan Dana", 
        "tombol" : "Tambah Penerimaan",
        "form": form, 
        "datas": penerimaan_list,
        # "subtotal_list": subtotal_list,
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
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url)


