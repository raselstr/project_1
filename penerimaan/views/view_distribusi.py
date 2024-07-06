from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from collections import defaultdict
from django.contrib import messages

from .. models import DistribusiPenerimaan
from .. forms import DistribusiForm

Form_data = DistribusiForm
Model_data = DistribusiPenerimaan
lokasitemplate = 'distribusi/distribusi_list.html'
lokasiupdate = 'distribusi/distribusi_form.html'
tag_url = 'list_distibusi'

def list(request):
    
    data = Model_data.objects.all().order_by('distri_penerimaan')
    context = {
        "judul": "Daftar Distribusi Penerimaan Dana", 
        "tombol" : "Tambah Distribusi Dana",
        "datas": data,
        # "subtotal_list": subtotal_list,
        # "total": total,
        
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


